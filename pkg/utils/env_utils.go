package utils

import (
	"log"
	"os"
	"strings"
)

func MustGetEnv(envVar string) string {
	value, isSet := os.LookupEnv("envVar")
	if !isSet || strings.TrimSpace(value) == "" {
		log.Fatalf("Mandatory environment variable %s not set...", envVar)
	}

	return value
}
