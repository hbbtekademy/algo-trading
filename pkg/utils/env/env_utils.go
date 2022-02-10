package envutils

import (
	"log"
	"os"
	"strings"
)

func MustGetEnv(envVar string) string {
	value, isSet := os.LookupEnv(envVar)
	if !isSet || strings.TrimSpace(value) == "" {
		log.Fatalf("Mandatory environment variable %s not set...", envVar)
	}

	return value
}

func GetEnv(envVar string, defaultValue string) string {
	value, isSet := os.LookupEnv(envVar)
	if !isSet || strings.TrimSpace(value) == "" {
		return defaultValue
	}

	return value
}

func IsLocalEnv() bool {
	localDev := GetEnv("LOCAL_DEV", "false")
	if localDev == "true" {
		return true
	}

	return false
}
