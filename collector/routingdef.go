package main

import (
	"log"
	"encoding/json"
	"regexp"
)

const URL_SOURCE = "url"

type Route struct {
	IsUnconditional bool   `yaml:"-"`
	Source string          `yaml:"source"`
	SourceIsURL bool       `yaml:"-"`
	Filter string          `yaml:"filter"`
	FilterR *regexp.Regexp `yaml:"-"`
	Topic string           `yaml:"topic"`
	Final bool             `yaml:"final"`
}

type Meta struct {
	Source string    `yaml:"source"`
	SourceIsURL bool `yaml:"-"`
	Meta string      `yaml:"meta"`
}

type RoutingDef struct {
	UnroutedTopic string `yaml:"unroutedTopic"`
	Routing []Route      `yaml:"routing"`
	Meta []Meta          `yaml:"meta"`
}

func (self *RoutingDef) initDefaultRouting(strDef string) {
	err := json.Unmarshal([]byte(strDef), &self.Routing)
	if err!=nil {
		log.Fatal("Could not parse routing: %v", err)
	}
}

func (self *RoutingDef) compileRouting() {
	for i, route := range self.Routing {
		if route.Source=="" {
			if (route.Filter!="") || (route.Topic=="") {
				log.Fatal("Invalid route definition: %v", route)
			}
			self.Routing[i].IsUnconditional = true
		} else {
			if route.Topic=="" {
				route.Topic = "$0"
			}
			if route.Filter=="" {
				route.Filter = ".*"
			}
			self.Routing[i].FilterR = regexp.MustCompile(route.Filter)
			self.Routing[i].SourceIsURL = (route.Source==URL_SOURCE)
		}
	}
}

func (self *RoutingDef) showRouting() {
	for i, route := range self.Routing {
		if route.Source=="" {
			log.Printf(" Route[%d]: always => topic(%s)\n", i, route.Topic)
		} else {
			log.Printf(" Route[%d]: header(%s) => filter(%s) => topic(%s)%s\n", i, route.Source, route.Filter, route.Topic, func() string {if route.Final {return " => final"} else {return ""}}())
		}
	}
}

func (self *RoutingDef) initDefaultMeta(strDef string) {
	err := json.Unmarshal([]byte(strDef), &self.Meta)
	if err!=nil {
		log.Fatal("Could not parse meta: %v", err)
	}
}

func (self *RoutingDef) compileMeta() {
	for i, meta := range self.Meta {
		self.Meta[i].SourceIsURL = (meta.Source==URL_SOURCE)
	}
}

func (self *RoutingDef) showMeta() {
	for i, meta := range self.Meta {
		log.Printf(" Meta[%d]: header(%s) => meta(%s)\n", i, meta.Source, meta.Meta)
	}
}

func (self *RoutingDef) show() {
	self.showRouting()
	if self.UnroutedTopic=="" {
		log.Printf(" Route[unrouted]: none\n",)
	} else {
		log.Printf(" Route[unrouted]: topic(%s)\n", self.UnroutedTopic)
	}
	self.showMeta()
}
