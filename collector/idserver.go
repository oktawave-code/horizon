package main

import (
	"log"
        "crash.ops.oktawave.com/git/scm/hor/idserverlink.git"
)
type IDServer struct {
	active bool
	Status string
	link *idserverlink.IDServer
	tokenHeader string
	clientId string
	backdoorToken string
}

func (self *IDServer) Init(config *Config) {
	if config.Settings["ID_SERVER_URL"]=="" {
		log.Printf("Id server disabled")
		return
	}
	self.active = true
	self.link = idserverlink.New(config.Settings["ID_SERVER_URL"])
	self.link.FuckedUpServer = true // Activate nastiness
	self.Status = ""
	if !self.link.TestConnection() {
		self.Status = "Connection test failed"
	}
	log.Printf("Client id: %v", config.Settings["CLIENT_ID"])
	self.tokenHeader = config.Settings["TOKEN_HEADER"]
	self.clientId = config.Settings["CLIENT_ID"]
	self.backdoorToken = config.Settings["BACKDOOR_TOKEN"]
}

func (self *IDServer) GetClientId(token string) (string, error) {
	id, err := self.link.GetClientId(token)
	if err==nil {
		self.Status = ""
	} else {
		self.Status = err.Error()
	}
	return id, err
}
