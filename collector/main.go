package main

func main() {
	var config Config
	var idServer IDServer
	var output Output
	var server Server

	config.Init()
	idServer.Init(&config)
	output.Init(&config)
	server.Init(&config)

	server.Serve(&idServer, &output)
}
