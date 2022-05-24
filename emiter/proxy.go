package main

// TODO zrobić coś ze / w routingu
// TODO posbyć się do końca panic()
// TODO 403 zawsze baz tokena
// TODO timeout na http server
// TODO zastanowić się co z kolejnąścią reguł routingu i ich wzajemnym przesłanianiem

import (
	"crash.ops.oktawave.com/git/scm/hor/idserverlink.git"
	"errors"
	"fmt"
	"github.com/go-redis/redis"
	"github.com/gorilla/mux"
	"gopkg.in/yaml.v2"
	"io/ioutil"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
)

const POST_NO_TOKEN_ERR = "No token header.\n"
const POST_WRONG_TOKEN_ERR = "Wrong token.\n"
const POST_INTERNAL_ERR = "Internal error.\n"

// Config

var defaultSettings = map[string]string{
	"LISTEN_PORT":         "80",
	"CLIENT_ID":           "?",
	"ID_SERVER_URL":       "",
	"TOKEN_HEADER":        "X-Token",
	"BACKEND_ELASTIC":     "",
	"BACKEND_REDIS":       "",
	"OCS_AUTH_URL":        "",
	"OCS_USER":            "",
	"OCS_PASS":            "",
	"ROUTING_FILE":        "",
	"HTTP_CLIENT_TIMEOUT": "10",
	"BACKDOOR_TOKEN":      "",
}

type Config struct {
	Settings map[string]string
}

func (self *Config) Init() {
	var found bool
	self.Settings = make(map[string]string)
	for k, v := range defaultSettings {
		self.Settings[k], found = os.LookupEnv(k)
		if !found {
			self.Settings[k] = v
		}
	}
}

// Routing

type Rule struct {
	Name string `yaml:"name"`
	Type string `yaml:"type"`
	Src  string `yaml:"src"`
	Dst  string `yaml:"dst"`
}

type Routing struct {
	Rules []Rule `yaml:"rules"`
}

// IDServer

type IDServer struct {
	active        bool
	link          *idserverlink.IDServer
	tokenHeader   string
	clientId      string
	backdoorToken string
}

func (self *IDServer) Init(config Config) {
	if config.Settings["ID_SERVER_URL"] == "" {
		log.Println("Id server disabled")
		return
	}
	self.active = true
	self.link = idserverlink.New(config.Settings["ID_SERVER_URL"])
	self.link.FuckedUpServer = true
	log.Printf("Client id: %v", config.Settings["CLIENT_ID"])
	self.tokenHeader = config.Settings["TOKEN_HEADER"]
	self.clientId = config.Settings["CLIENT_ID"]
	self.backdoorToken = config.Settings["BACKDOOR_TOKEN"]
}

func (self *IDServer) GetClientId(token string) (string, error) {
	return self.link.GetClientId(token)
}

// Transport // do obsługi 401 w ocs

type OCStransport struct {
	http.RoundTripper
	ProxySrv
}

func (self *OCStransport) RoundTrip(req *http.Request) (resp *http.Response, err error) {
	resp, err = self.RoundTripper.RoundTrip(req)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode == 401 {
		self.ProxySrv.OCSAuthOnce()
		if self.ProxySrv.ocsStUrl == "" {
			return nil, err
		}
		return self.reRequest(req)
	}
	return resp, nil
}

func (self *OCStransport) reRequest(r *http.Request) (resp *http.Response, err error) {
	client := &http.Client{Timeout: self.ProxySrv.httpClientTimeout}
	// to jest rzeżba na całego, jako że nie mam skąd wziąć ładnego URL-a do zapytania muszę go sobie pociąć.
	// w r.URL.Path mam /v1/stary_Storage-Url/włąściwa_część
	// poniżej w brzydki sposób wycinam /v1/stary_Storage-Url/
	nUrl := r.URL.Path
	nUrl = nUrl[strings.Index(nUrl, "/")+1:]
	nUrl = nUrl[strings.Index(nUrl, "/")+1:]
	nUrl = nUrl[strings.Index(nUrl, "/")+1:]
	req, err := http.NewRequest("GET", self.ProxySrv.ocsStUrl+"/"+nUrl, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Add("X-Auth-Token", self.ProxySrv.ocsToken)
	resp, err = client.Do(req)
	if err != nil {
		return nil, err
	}
	return resp, nil
}

// Switch Handler // do podniany routingu w locie

type SwitchHandler struct {
	router http.Handler
}

func (self *SwitchHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	self.router.ServeHTTP(w, r)
}

// ProxySrv

type ProxySrv struct {
	config                  Config
	idServer                IDServer
	handler                 *SwitchHandler
	elasticProxy            *httputil.ReverseProxy
	ocsProxy                *httputil.ReverseProxy
	ocsToken                string
	ocsStUrl                string
	ocsLock                 sync.Mutex
	ocsLockid               int64
	httpClientTimeout       time.Duration
	traceFirstBackdoorToken bool
}

func (self *ProxySrv) Init() {
	self.config.Init()
	httpClientTimeout, err := strconv.Atoi(self.config.Settings["HTTP_CLIENT_TIMEOUT"])
	if err != nil {
		log.Println("Invalid value of HTTP_CLIENT_TIMEOUT env, int expected, default 10s is set")
		self.httpClientTimeout = time.Duration(10) * time.Second
	} else {
		self.httpClientTimeout = time.Duration(httpClientTimeout) * time.Second
	}
	self.idServer.Init(self.config)
	self.InitElasticProxy()
	self.ocsLockid = time.Now().UnixNano()
	self.InitOCSProxy()
	self.handler = &SwitchHandler{}
	self.traceFirstBackdoorToken = true
	err = self.InitRouter()
	if err != nil {
		log.Println(err)
		log.Fatal("Can't config routing, Exiting")
	}
	go self.configWatcher()
}

func (self *ProxySrv) configWatcher() {
	prevStat, err := os.Stat(self.config.Settings["ROUTING_FILE"])
	if err != nil {
		log.Fatal("Can not access config file: %f", err)
	}
	for {
		stat, err := os.Stat(self.config.Settings["ROUTING_FILE"])
		if err == nil {
			if (stat.Size() != prevStat.Size()) || (stat.ModTime() != prevStat.ModTime()) {
				log.Println("New routing found")
				prevStat, err = os.Stat(self.config.Settings["ROUTING_FILE"])
				err := self.InitRouter()
				prevStat = stat
				if err != nil {
					log.Println("Can't config new routing, old routing stay in use")
				} else {
					log.Println("New routing loaded")
				}
			}
		}
		time.Sleep(time.Second)
	}
}

func (self *ProxySrv) InitRouter() error {
	filename := self.config.Settings["ROUTING_FILE"]
	var routing Routing
	source, err := ioutil.ReadFile(filename)
	if err != nil {
		return errors.New("Error while read routing config file: " + err.Error())
	}
	err = yaml.Unmarshal(source, &routing)
	if err != nil {
		return errors.New("Error while parsing routing config file: " + err.Error())
	}
	newRouter := mux.NewRouter()
	// Tu normalizuje / w Src i Dst
	for k, _ := range routing.Rules {
		routing.Rules[k].Src = "/" + strings.Trim(routing.Rules[k].Src, "/")
		routing.Rules[k].Dst = "/" + strings.Trim(routing.Rules[k].Src, "/")
		if strings.Compare(routing.Rules[k].Src, "/") == 0 {
			routing.Rules[k].Src = ""
		}
		if strings.Compare(routing.Rules[k].Dst, "/") == 0 {
			routing.Rules[k].Dst = ""
		}
	}
	// Tu sortuje po Src od najdłuższego do najkrótszego
	sort.Slice(routing.Rules, func(i, j int) bool {
		return len(routing.Rules[i].Src) > len(routing.Rules[j].Src)
	})
	for _, rule := range routing.Rules {
		switch rule.Type {
		case "elasticsearch":
			newRouter.HandleFunc(rule.Src+"/{query:.*}", self.ElasticFactory(rule.Dst)).Methods("GET")
			log.Println("Add new route elasticsearch: " + rule.Src + "/{query:.*} >>> " + rule.Dst)
		case "redis":
			newRouter.HandleFunc(rule.Src+"/{query:.*}", self.RedisFactory()).Methods("GET")
			log.Println("Add new route redis: " + rule.Src + "/{query:.*} >>> ")
		case "ocs":
			newRouter.HandleFunc(rule.Src+"/{query:.*}", self.OCSFactory(rule.Dst)).Methods("GET")
			log.Println("Add new route ocs: " + rule.Src + "/{query:.*} >>> " + rule.Dst)
		}
	}
	newRouter.HandleFunc("/{query.*}", self.NoFoundFactory())
	newRouter.Use(self.AuthFactory)
	self.handler.router = newRouter
	return nil
}

func (self *ProxySrv) OCSAuth() {
	client := &http.Client{Timeout: self.httpClientTimeout}
	req, err := http.NewRequest("GET", self.config.Settings["OCS_AUTH_URL"], nil)
	if err != nil {
		self.ocsStUrl = ""
		self.ocsToken = ""
		return
	}
	req.Header.Add("X-Auth-User", self.config.Settings["OCS_USER"])
	req.Header.Add("X-Auth-Key", self.config.Settings["OCS_PASS"])
	resp, err := client.Do(req)
	if err != nil {
		self.ocsStUrl = ""
		self.ocsToken = ""
		return
	}
	defer resp.Body.Close()
	self.ocsStUrl = resp.Header["X-Storage-Url"][0]
	self.ocsToken = resp.Header["X-Auth-Token"][0]
}

func (self *ProxySrv) OCSAuthOnce() {
	nowid := self.ocsLockid
	self.ocsLock.Lock()
	if nowid == self.ocsLockid {
		self.OCSAuth()
		if self.ocsStUrl != "" {
			self.ocsLockid = time.Now().UnixNano()
		}
	}
	self.ocsLock.Unlock()
}

func (self *ProxySrv) InitOCSProxy() error {
	if strings.Compare(self.config.Settings["OCS_AUTH_URL"], "") == 0 {
		return errors.New("Can not init OCSProxy, OCS_AUTH_URL not set")
	}
	if strings.Compare(self.config.Settings["OCS_USER"], "") == 0 {
		return errors.New("Can not init OCSProxy, OCS_USER not set")
	}
	if strings.Compare(self.config.Settings["OCS_PASS"], "") == 0 {
		return errors.New("Can not init OCSProxy, OCS_PASS not set")
	}
	self.OCSAuthOnce()
	remote, err := url.Parse(self.ocsStUrl)
	if err != nil {
		return errors.New("Can not init OCSProxy, parse ocs storage url error: " + err.Error())
	}
	self.ocsProxy = httputil.NewSingleHostReverseProxy(remote)
	self.ocsProxy.Transport = &OCStransport{http.DefaultTransport, *self}
	return nil
}

func (self *ProxySrv) OCSFactory(dst string) http.HandlerFunc {
	url, _ := url.Parse(self.ocsStUrl)
	host := url.Hostname()
	return func(w http.ResponseWriter, r *http.Request) {
		if self.ocsStUrl == "" {
			self.OCSAuthOnce()
		}
		r.Header.Set("X-Auth-Token", self.ocsToken)
		r.Host = host
		r.URL.Path = dst + "/" + mux.Vars(r)["query"]
		self.ocsProxy.ServeHTTP(w, r)
	}
}

func (self *ProxySrv) InitElasticProxy() error {
	target := "http://" + self.config.Settings["BACKEND_ELASTIC"]
	remote, err := url.Parse(target)
	if err != nil {
		return errors.New("Can not init ElasticProxy, parse BACKEND_ELASTIC url error: " + err.Error())
	}
	self.elasticProxy = httputil.NewSingleHostReverseProxy(remote)
	return nil
}

func (self *ProxySrv) ElasticFactory(dst string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		r.URL.Path = dst + "/" + mux.Vars(r)["query"]
		self.elasticProxy.ServeHTTP(w, r)
	}
}

func (self *ProxySrv) RedisFactory() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		key := mux.Vars(r)["query"]
		client := redis.NewClient(&redis.Options{
			Addr:     self.config.Settings["BACKEND_REDIS"],
			Password: "",
			DB:       0,
		})
		val, err := client.Get(key).Result()
		if err != nil {
			if err.Error() == "redis: nil" {
				http.NotFound(w, r)
			} else {
				http.Error(w, err.Error(), 502)
			}
			return
		}
		fmt.Fprintf(w, "%s\n", val)
	}
}

func (self *ProxySrv) AuthFactory(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if self.idServer.active {
			tokens, found := r.Header[self.idServer.tokenHeader]
			if !found {
				http.Error(w, POST_NO_TOKEN_ERR, 401)
				return
			}
			if (self.idServer.backdoorToken != "") && (self.idServer.backdoorToken == tokens[0]) {
				if self.traceFirstBackdoorToken {
					log.Printf("Backdoor token used\n")
					self.traceFirstBackdoorToken = false
				}
			} else {
				id, err := self.idServer.GetClientId(tokens[0])
				if err != nil {
					log.Printf("Internal error: %v\n", err)
					http.Error(w, POST_INTERNAL_ERR, 500)
					return
				}
				if id != self.idServer.clientId {
					log.Printf("Wrong token: %v != %v\n", id, self.idServer.clientId)
					http.Error(w, POST_WRONG_TOKEN_ERR, 401)
					return
				}
			}
		}
		next.ServeHTTP(w, r)
	})
}

func (self *ProxySrv) NoFoundFactory() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		http.NotFound(w, r)
	}
}

func (self *ProxySrv) Start() {
	http.Handle("/", self.handler)
	log.Fatal(http.ListenAndServe(":"+self.config.Settings["LISTEN_PORT"], nil))
}

func main() {
	var proxysrv ProxySrv
	proxysrv.Init()
	proxysrv.Start()
}
