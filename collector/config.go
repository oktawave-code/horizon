package main

import (
	"log"
	"os"
	"time"
	"io/ioutil"
	"gopkg.in/yaml.v2"
	"sync/atomic"
)

var defaultSettings = map[string]string{
	// General settings
	"LISTEN_PORT":             "80",
	"CLIENT_ID":               "?",
	"TOKEN_HEADER":            "X-Token",
	"ID_SERVER_URL":           "",
	"BACKDOOR_TOKEN":          "",
	"KAFKA_BOOTSTRAP_SERVER":  "",
	"VERBOSE":                 "",
	"SKIP_META":               "",
	"CONFIG_FILE":             "",
	"SARAMA_MAX_REQUEST_SIZE": "1048576",
	// Routing defaults:
	"ROUTING":                 "[]",
	"UNROUTED_TOPIC":          "",
	"META":                    "[]",
}

type Config struct {
	Settings map[string]string
	routingDef atomic.Value
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
	newRoutingDef := self.loadConfigFile()
	newRoutingDef.show()
	self.routingDef.Store(newRoutingDef)
	if self.Settings["CONFIG_FILE"]!="" {
		go self.configWatcher()
	}
}

func (self *Config) loadConfigFile() *RoutingDef {
	var newDef RoutingDef
	newDef.UnroutedTopic = self.Settings["UNROUTED_TOPIC"]
	newDef.initDefaultRouting(self.Settings["ROUTING"])
	newDef.initDefaultMeta(self.Settings["META"])
	defer newDef.compileRouting()
	defer newDef.compileMeta()
	if self.Settings["CONFIG_FILE"]=="" {
		log.Printf("Config file not used\n")
		return &newDef
	}
	cfgFile, err := ioutil.ReadFile(self.Settings["CONFIG_FILE"])
	if err!=nil {
		log.Printf("Failed to load config file: %v\n", err)
		return &newDef
	}

	err = yaml.Unmarshal(cfgFile, &newDef)
	if err!=nil {
		log.Printf("Failed to parse config file: %v\n", err)
	}
	return &newDef
}

func (self *Config) GetRoutingDef() *RoutingDef {
	return self.routingDef.Load().(*RoutingDef)
}

func (self *Config) configWatcher() {
	prevStat, err := os.Stat(self.Settings["CONFIG_FILE"])
	if err!=nil {
		log.Fatal("Can not access config file: %f", err)
	}
	for {
		stat, err := os.Stat(self.Settings["CONFIG_FILE"])
		if err==nil {
			if (stat.Size()!=prevStat.Size()) || (stat.ModTime()!=prevStat.ModTime()) {
				log.Printf("Reloading routing config...\n")
				newRoutingDef := self.loadConfigFile()
				newRoutingDef.show()
				self.routingDef.Store(newRoutingDef)
				prevStat = stat
			}
		}
		time.Sleep(time.Second)
	}
}
