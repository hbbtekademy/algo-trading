package tokenservice

import (
	"log"
	"net/http"
	"os"
)

var (
	requestToken string
)

func Start() {
	log.Println("Starting token service")

	http.HandleFunc("/token", tokenHandler)
	http.HandleFunc("/local", localTokenHandler)
	http.HandleFunc("/", localBreezeTokenHandler)
	http.HandleFunc("/sensor-data", localSensorData)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
		log.Printf("Defaulting to port %s", port)
	}

	log.Printf("Listening on port %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Println("Error in ListenAndServe")
		log.Fatal(err)
	}
}
