package main

import (
	"io"
	"io/ioutil"
	"net/http"
	"log"
	"fmt"
	"strconv"
)

const GET_MSG = "Horizon collector digestive track entry. Omnomnom.\n"
const GET_STATUS_OK_MSG = "Ok.\n"
const GET_STATUS_ERR_MSG = "Definitely not ok.\n"
const POST_NO_TOKEN_ERR = "No token header.\n"
const POST_WRONG_TOKEN_ERR = "Wrong token.\n"
const POST_INTERNAL_ERR = "Internal error.\n"
const POST_OK_MSG = "Consumed.\n"

type Server struct {
	traceFirstRequest bool
	traceFirstBackdoorToken bool
	port int
	verbose bool
	config *Config
}

func (self *Server) Init(config *Config) {
	self.traceFirstRequest = true
	self.traceFirstBackdoorToken = true
	self.config = config
	self.verbose = (config.Settings["VERBOSE"]!="")
	port, err := strconv.Atoi(config.Settings["LISTEN_PORT"])
	if err != nil {
		log.Fatal("Port format error: %v\n", err)
	}
	self.port = port
	log.Printf("Listen port: %d\n", self.port)
}

func (self *Server) HandlerFactory(idServer *IDServer, output *Output) http.HandlerFunc {

	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method=="POST" {
			if self.traceFirstRequest {
				log.Printf("Packet from: %v\n", r.RemoteAddr)
			}
			var topics []string
			if idServer.active {
				tokens, found := r.Header[idServer.tokenHeader]
				if !found {
					http.Error(w, POST_NO_TOKEN_ERR, 401)
					return
				}
				if (idServer.backdoorToken!="") && (idServer.backdoorToken==tokens[0]) {
					if (self.traceFirstRequest){
						log.Printf("Backdoor token used\n")
						self.traceFirstBackdoorToken = false
					}
				} else {
					id, err := idServer.GetClientId(tokens[0])
					if err!=nil {
						log.Printf("Internal error: %v\n", err)
						http.Error(w, POST_INTERNAL_ERR, 500)
						return
					}
					if id != idServer.clientId {
						log.Printf("Wrong token: %v != %v\n", id, idServer.clientId)
						http.Error(w, POST_WRONG_TOKEN_ERR, 401)
						return
					}
				}
			}
			body, err := ioutil.ReadAll(r.Body)
			if err!=nil {
				log.Printf("Request body read error: %v\n", err)
				http.Error(w, POST_INTERNAL_ERR, 500)
				return
			}
			if self.traceFirstRequest {
				log.Printf("Body size: %d\n", len(body))
			}
			routingDef := self.config.GetRoutingDef()
			topics, err = output.Route(routingDef, r.URL, r.Header, body)
			if err!=nil {
				http.Error(w, POST_INTERNAL_ERR, 500)
				return
			}
			io.WriteString(w, POST_OK_MSG)
			if self.traceFirstRequest || self.verbose {
				for _, topic := range topics {
				log.Printf(" => \"%s\"\n", topic)
				}
			}
		} else if r.Method=="GET" {
			if r.URL.Path=="/status" {
				if (output.Status=="") && (idServer.Status=="") {
					io.WriteString(w, GET_STATUS_OK_MSG)
				} else {
					io.WriteString(w, GET_STATUS_ERR_MSG)
					if self.verbose {
						io.WriteString(w, fmt.Sprintf("output: %s\nidServer: %s\n", output.Status, idServer.Status))
					}
				}
			} else if r.URL.Path=="/stats" {
				if idServer.active {
					io.WriteString(w, fmt.Sprintf("%+v\n", idServer.link.Cache.Stats))
					io.WriteString(w, fmt.Sprintf("%+v\n", idServer.link.Stats))
				}
			} else {
				io.WriteString(w, GET_MSG)
			}
		} else if r.Method=="HEAD" {
			// TODO
		}
		self.traceFirstRequest = false
	}
}

func (self *Server) Serve(idServer *IDServer, output *Output) {
	var handler = self.HandlerFactory(idServer, output)
	http.HandleFunc("/", handler)
	log.Printf("Listening...\n")
	log.Fatal(http.ListenAndServe(":"+strconv.Itoa(self.port), nil))
}
