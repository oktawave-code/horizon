package genericcache

import (
	"time"
	"sync"
	"runtime"
)

/*
	Generic caching facility


	0               freshDuration     ttl
	|               |                 |
	+---------------+-----------------+-------------->
	 return value    spawn resolver    spawn resolver
	 from cache      and immediately   and wait for
	                 return value      new value
	                 from cache
	
*/

type Item interface{}

type ResolverCallback func(context interface{}, key string, pendingResolves int) Item

type Stats struct {
	Requests int64
    CacheHits int64
    CacheMiss int64
	InitialResolves int64
	RollingResolves int64
	OutdatedResolves int64
	MaxPendingResolves int
	DeletedEntries int64
}

type Cache struct {
	context interface{}
	resolver ResolverCallback
	cache map[string] cacheRecord
	lock sync.Mutex
	pendingResolves int
	freshDuration time.Duration
	ttl time.Duration
	cleanupInterval time.Duration
	stopCleanup chan bool
	Stats Stats
}

type cacheRecord struct {
	value Item
	t time.Time
	waitChan *chan struct{}
}

var zeroTime = time.Time{}

func cleanupStopper(c *Cache) {
	c.stopCleanup <- true
}

func (self *Cache) Init(context interface{}, resolver ResolverCallback) {
	self.context = context
	self.resolver = resolver
	self.cache = make(map[string] cacheRecord)
	self.freshDuration = 100*time.Second
	self.ttl = 120*time.Second
	self.cleanupInterval = 10*time.Second
	runtime.SetFinalizer(self, cleanupStopper)
	go self.cleanupLoop()
}

func (self *Cache) cleanupLoop() {
	ticker := time.NewTicker(self.cleanupInterval)
	for {
		select{
		case <-ticker.C:
			self.cleanup()
		case <-self.stopCleanup:
			ticker.Stop()
			return
		}
	}
}

func (self *Cache) cleanup() {
	now := time.Now()
	self.lock.Lock()
	for k, v := range self.cache {
		if (v.t!=zeroTime) && (now.Sub(v.t)>self.ttl) && (v.waitChan==nil) {
			delete(self.cache, k)
			self.Stats.DeletedEntries += 1
		}
	}
	self.lock.Unlock()
}

func (self *Cache) Get(key string) Item {
	var waitChan *chan struct{}
	now := time.Now()
	self.lock.Lock()
	self.Stats.Requests += 1
	rec, found := self.cache[key]
	if !found { // Not in cache: add placeholder, spawn request and wait
		waitChan = new(chan struct{})
		*waitChan = make(chan struct{})
		self.cache[key] = cacheRecord{"", zeroTime, waitChan}
	    self.Stats.CacheMiss += 1
		self.pendingResolves += 1
		self.Stats.InitialResolves += 1
		self.lock.Unlock()
		go self.resolve(key)
		return self.wait(key, waitChan)
	}
	age := now.Sub(rec.t)
	if age<self.freshDuration { // Fresh and juicy: just return cached value
		self.lock.Unlock()
	    self.Stats.CacheHits += 1
		return rec.value
	}
	if age<self.ttl { // Good enough: spawn request and return cached value
		if rec.waitChan!=nil {
			self.lock.Unlock()
			return rec.value // already resolving, just return
		}
		waitChan = new(chan struct{})
		*waitChan = make(chan struct{})
		self.cache[key] = cacheRecord{rec.value, rec.t, waitChan}
		self.pendingResolves += 1
		self.Stats.RollingResolves += 1
		self.lock.Unlock()
		go self.resolve(key)
		return rec.value
	}
	if rec.waitChan!=nil { // Already resolving: just wait
		waitChan = rec.waitChan // copy it inside mutex lock - it might dissapear outside of it
		self.lock.Unlock()
		return self.wait(key, waitChan) // already resolving, just wait
	}
	// Outdated: replace with placeholder, spawn request and wait
	waitChan = new(chan struct{})
	*waitChan = make(chan struct{})
	self.cache[key] = cacheRecord{"", zeroTime, waitChan}
	self.pendingResolves += 1
	self.Stats.OutdatedResolves += 1
	self.Stats.CacheMiss += 1
	self.lock.Unlock()
	go self.resolve(key)
	return self.wait(key, waitChan)
}

func (self *Cache) resolve(key string) {
	value := self.resolver(self.context, key, self.pendingResolves)
	self.lock.Lock()
	if self.pendingResolves>self.Stats.MaxPendingResolves {
		self.Stats.MaxPendingResolves = self.pendingResolves
	}
	self.pendingResolves -= 1
	waitChan := self.cache[key].waitChan
	self.cache[key] = cacheRecord{value, time.Now(), nil}
	self.lock.Unlock()
	close(*waitChan)
}

func (self *Cache) wait(key string, waitChan *chan struct{}) Item {
	<- *waitChan
	self.lock.Lock()
	rec := self.cache[key]
	self.lock.Unlock()
	return rec.value
}

func New(context interface{}, resolver ResolverCallback) *Cache {
	var c *Cache = new(Cache)
	c.Init(context, resolver)
	return c
}
