package main

import (
	"net/url"
	"strings"
	"github.com/Shopify/sarama"
	"log"
	"fmt"
	"net/http"
	"strconv"
)

type Output struct {
	active bool
	Status string
	verbose bool
	skipMeta bool
	unroutedTopic string
	producer sarama.SyncProducer
	saramaMaxRequestSize int
}

func (self *Output) Init(config *Config) {
	self.verbose = (config.Settings["VERBOSE"]!="")
	self.skipMeta = (config.Settings["SKIP_META"]!="")
	if config.Settings["KAFKA_BOOTSTRAP_SERVER"]=="" {
		log.Printf("No Kafka connection defined")
		return
	}
	if self.verbose {
		log.Printf("Verbose mode on")
	}
	if self.skipMeta {
		log.Printf("Metadata forwarding disabled")
	}
	log.Printf("Kafka server: %v", config.Settings["KAFKA_BOOTSTRAP_SERVER"])
	self.active = true
	self.Status = ""
	sCfg := sarama.NewConfig()
	sCfg.ClientID = "Collector"
	sCfg.Producer.RequiredAcks = sarama.WaitForAll
	sCfg.Producer.Retry.Max = 10
	sCfg.Producer.Return.Successes = true
	sCfg.Producer.MaxMessageBytes = 15000000
	saramaMaxRequestSize, err := strconv.Atoi(config.Settings["SARAMA_MAX_REQUEST_SIZE"])
	sarama.MaxRequestSize = int32(saramaMaxRequestSize)
	producer, err := sarama.NewSyncProducer([]string{config.Settings["KAFKA_BOOTSTRAP_SERVER"],}, sCfg)
	if err!=nil {
		log.Fatal("Failed to start Sarama producer: %s", err)
	}
	self.producer = producer
}

func (self *Output) Route(routingDef *RoutingDef, url *url.URL, header http.Header, body []byte) ([]string, error) {
	routed := false
	topics := make([]string, 0)
	for _, route := range routingDef.Routing {
		var topic string
		if route.IsUnconditional {
			topic = route.Topic
		} else {
			var source string
			if route.SourceIsURL {
				source = url.Path // TODO: host? query? fragment?
			} else {
				sourcesList, found := header[route.Source]
				if !found {
					continue
				}
				source = sourcesList[0]
			}
			matches := route.FilterR.FindStringSubmatch(source)
			if len(matches)>0 {
				repl := make([]string, len(matches)*2)
				for i, m := range matches {
					repl = append(repl, "$"+strconv.Itoa(i), m)
				}
				replacer := strings.NewReplacer(repl...)
				topic = replacer.Replace(route.Topic) // TODO: Can be done faster
			}
		}
		if topic!="" {
			topics = append(topics, topic)
			routed = true
			if route.Final {
				break
			}
		}
	}
	if (!routed) && (routingDef.UnroutedTopic!="") {
		topics = append(topics, routingDef.UnroutedTopic)
	}
	errState := false
	if (len(topics)>0) && (self.active) {
		bodyVal := sarama.StringEncoder(body)
		msgs := make([]*sarama.ProducerMessage, len(topics))
		if !self.skipMeta {
			headers := make([]sarama.RecordHeader, len(routingDef.Meta))
			for i, meta := range routingDef.Meta {
				headers[i].Key = []byte(meta.Meta)
				if meta.SourceIsURL {
					headers[i].Value = []byte(url.Path) // TODO: host? query? fragment?
				} else {
					val, found := header[meta.Source]
					if found {
						headers[i].Value = []byte(val[0])
					} else {
						headers[i].Value = []byte("")
					}
				}
			}
			for i, topic := range topics {
				msgs[i] = &sarama.ProducerMessage{
					Topic: topic,
					Value: bodyVal,
					Headers: headers,
				}
			}
		} else {
			for i, topic := range topics {
				msgs[i] = &sarama.ProducerMessage{
					Topic: topic,
					Value: bodyVal,
				}
			}
		}
		errs := self.producer.SendMessages(msgs)
		if errs!=nil {
			log.Printf("SendMessage error: %v", errs)
			for _, err := range errs.(sarama.ProducerErrors) {
				log.Printf(" %v", err)
			}
			errState = true
		}
	}
	if errState {
		self.Status = "SendMessage problem"
		return topics, fmt.Errorf("SendMessage error")
	}
	self.Status = ""
	return topics, nil
}
