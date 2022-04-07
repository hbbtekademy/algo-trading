package secretmanager

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"

	secretmanager "cloud.google.com/go/secretmanager/apiv1"
	secretmanagerpb "google.golang.org/genproto/googleapis/cloud/secretmanager/v1"
	envutils "org.hbb/algo-trading/go/pkg/utils/env"
)

const (
	KiteApiKeySK      string = "KITE_API_KEY"
	KiteApiSecretSK   string = "KITE_API_SECRET"
	KiteAccessTokenSK string = "KITE_ACCESS_TOKEN"
)

func GetSecret(keyName string) string {

	if envutils.IsLocalEnv() {
		return envutils.MustGetEnv(keyName)
	}

	ctx := context.Background()
	client := getClient()
	defer client.Close()

	accessRequest := &secretmanagerpb.AccessSecretVersionRequest{
		Name: fmt.Sprintf("projects/%s/secrets/%s/versions/latest", getProjectId(), keyName),
	}

	result, err := client.AccessSecretVersion(ctx, accessRequest)
	if err != nil {
		log.Fatalf("failed to access secret version: %v", err)
	}

	return string(result.Payload.Data)
}

func CreateSecret(key string, value string) error {
	ctx := context.Background()
	client := getClient()
	defer client.Close()

	if !secretExists(key) {
		log.Println("Secret doesnt exist. Creating it now...")
		createSecretReq := &secretmanagerpb.CreateSecretRequest{
			Parent:   fmt.Sprintf("projects/%s", getProjectId()),
			SecretId: key,
			Secret: &secretmanagerpb.Secret{
				Replication: &secretmanagerpb.Replication{
					Replication: &secretmanagerpb.Replication_Automatic_{
						Automatic: &secretmanagerpb.Replication_Automatic{},
					},
				},
			},
		}

		_, err := client.CreateSecret(ctx, createSecretReq)
		if err != nil {
			return err
		}
	}

	// Declare the payload to store.
	payload := []byte(value)

	// Build the request.
	addSecretVersionReq := &secretmanagerpb.AddSecretVersionRequest{
		Parent: fmt.Sprintf("projects/%s/secrets/%s", getProjectId(), key),
		Payload: &secretmanagerpb.SecretPayload{
			Data: payload,
		},
	}

	// Call the API.
	_, err := client.AddSecretVersion(ctx, addSecretVersionReq)
	if err != nil {
		return err
	}

	return nil
}

func getClient() *secretmanager.Client {
	ctx := context.Background()
	client, err := secretmanager.NewClient(ctx)
	if err != nil {
		log.Fatalln("Failed creating sceret manager client", err)
	}

	return client
}

func getProjectId() string {
	projectId, isSet := os.LookupEnv("GOOGLE_CLOUD_PROJECT")
	if !isSet || strings.TrimSpace(projectId) == "" {
		log.Fatalln("GOOGLE_CLOUD_PROJECT environment variable not set...")
	}

	return projectId
}

func secretExists(key string) bool {
	ctx := context.Background()
	client := getClient()
	defer client.Close()

	req := &secretmanagerpb.GetSecretRequest{
		Name: fmt.Sprintf("projects/%s/secrets/%s", getProjectId(), key),
	}

	_, err := client.GetSecret(ctx, req)
	if err != nil {
		return false
	}

	return true
}
