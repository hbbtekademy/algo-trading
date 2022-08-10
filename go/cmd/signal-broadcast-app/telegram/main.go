package main

import (
	"context"
	"log"
	"strconv"

	"github.com/go-redis/redis/v8"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
	envutils "org.hbb/algo-trading/go/pkg/utils/env"
	redisUtils "org.hbb/algo-trading/go/pkg/utils/redis"
)

var (
	redisClient *redis.Client
	ctx         context.Context
)

const (
	RedisTelegramChannel     string = "Smash-Telegram-Channel"
	EnvTelegramBotKey        string = "TELEGRAM_BOT_KEY"
	EnvTelegramChannelChatId string = "TELEGRAM_CHAT_ID"
)

var (
	TelegramChannelChatId = envutils.MustGetEnv(EnvTelegramChannelChatId)
	TelegramBotKey        = envutils.MustGetEnv(EnvTelegramBotKey)
)

func main() {

	initRedisClient()
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

	telegramBotApi := getTelegramBotApi()
	telegramChatIdAsInt := getTelegramChatId()

	for {
		messageFromRedisChannel, err := sub.ReceiveMessage(ctx)
		if err != nil {
			log.Fatal("Error receiving message")
		}
		log.Println("MessageFromRedisChannel received", messageFromRedisChannel)

		telegramMsg := NewMessage(telegramChatIdAsInt, messageFromRedisChannel.Payload)
		respMsg, err := telegramBotApi.Send(telegramMsg)

		if err != nil {
			log.Fatal("Error occurred while posting message to Telegram Channel: ", err)
		}

		log.Println("Message Published. Response from Telegram API: ", respMsg)
	}
}

func getTelegramChatId() int64 {
	telegramChatIdAsInt, err := strconv.ParseInt(TelegramChannelChatId, 0, 64)
	if err != nil {
		log.Fatal("Could not parse ChatId as Int", err)
	}
	return telegramChatIdAsInt
}

func getTelegramBotApi() *tgbotapi.BotAPI {
	telegramBotApi, err := tgbotapi.NewBotAPI(TelegramBotKey)
	if err != nil {
		log.Fatal("Could not create Telegram Bot API interface", err)
	}
	return telegramBotApi
}

func NewMessage(chatID int64, text string) tgbotapi.MessageConfig {
	return tgbotapi.MessageConfig{
		BaseChat: tgbotapi.BaseChat{
			ChatID:           chatID,
			ReplyToMessageID: 0,
		},
		Text:                  text,
		DisableWebPagePreview: false,
	}
}

func initRedisClient() {
	ctx = context.Background()
	redisClient = redisUtils.GetRTRedisClient()
}
