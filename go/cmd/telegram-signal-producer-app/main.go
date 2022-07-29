package main

import (
	"context"
	"github.com/go-redis/redis/v8"
	"log"
	"net/http"
	"net/url"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
)

var (
	redisClient *redis.Client
	ctx         context.Context
)

const (
	RedisTelegramChannel         string = "Smash-Telegram-Channel"
	TelegramApiUrl               string = "https://api.telegram.org/"
	TelegramBotKey               string = "bot5456571295:AAHi7TzIgns2pcipBC_xOjwgtSiVr-cI3lc"
	TelegramApiSendMessage       string = "/sendMessage"
	TelegramChannelChatIdKeyName string = "chat_id"
	TelegramChannelChatId        string = "-1001743840522"
	TelegramChannelTextKeyName   string = "text"
)

func main() {
	//0. connect to redis
	initRedisClient()
	//1. listen to redis message topic
	sub := redisClient.Subscribe(ctx, RedisTelegramChannel)
	iface, err := sub.Receive(ctx)

	if err != nil {
		log.Fatal("Error subscribing to Redis-Telegram channel")
	}

	switch iface.(type) {
	case *redis.Subscription:
		log.Println("subscribe succeeded")
	case *redis.Message:
		log.Println("received message")
	case *redis.Pong:
		log.Println("pong received")
	default:
		log.Fatal("Error in iface.type")
	}

	for {
		msg, err := sub.ReceiveMessage(ctx)
		if err != nil {
			log.Fatal("Error receiving message")
		}
		log.Println("Message received", msg)
		sendMessageToTelegramChannel(msg)
	}
}

func sendMessageToTelegramChannel(message *redis.Message) {
	data := url.Values{
		TelegramChannelChatIdKeyName: {TelegramChannelChatId},
		TelegramChannelTextKeyName:   {message.Payload},
	}

	resp, err := http.PostForm(TelegramApiUrl+TelegramBotKey+TelegramApiSendMessage, data)
	if err != nil {
		log.Fatal("Error occurred while posting message to Telegram Channel: ", err)
	}
	log.Println("Message published", resp)
}

func initRedisClient() {
	ctx = context.Background()
	redisClient = redisUtils.GetRTRedisClient()
}
