package redistypes

import (
	"fmt"
	"strconv"
	"strings"
	"time"
)

const (
	LtpKeyPrefix = "LTP:ts:sym:"
	LtpKeyFmt    = LtpKeyPrefix + "%s:%s"

	LtpIdxKeyPrefix = "IDX:LTP:sym:"
	LtpIdxKeyFmt    = LtpIdxKeyPrefix + "%s"

	VolKeyPrefix = "VOL:ts:sym:"
	VolKeyFmt    = VolKeyPrefix + "%s:%s"

	VolIdxKeyPrefix = "IDX:VOL:sym:"
	VolIdxKeyFmt    = VolIdxKeyPrefix + "%s"

	Cs1mKeyPrefix = "CS1M:ts:sym:"
	Cs1mKeyFmt    = Cs1mKeyPrefix + "%s:%s"

	Cs1mIdxKeyPrefix = "IDX:CS1M:sym:"
	Cs1mIdxKeyFmt    = Cs1mIdxKeyPrefix + "%s"

	Cs15mKeyPrefix = "CS15M:ts:sym:"
	Cs15mKeyFmt    = Cs15mKeyPrefix + "%s:%s"

	Cs15mIdxKeyPrefix = "IDX:CS15M:sym:"
	Cs15mIdxKeyFmt    = Cs15mIdxKeyPrefix + "%s"

	KeyTsFmt = "200601021504"

	Cs1mNotifyTopic  = "CS1M_NOTIFY"
	Cs15mNotifyTopic = "CS15M_NOTIFY"
)

type RedisKey struct {
	formatter string
	ts        string
	tokenId   string
	TS        time.Time
	TokenId   uint32
}

type RedisIdxKey struct {
	formatter string
	tokenId   string
	TokenId   uint32
}

func NewKeyPattern(ts string, tokenId string) RedisKey {
	return RedisKey{
		ts:      ts,
		tokenId: tokenId,
	}
}

func NewKey(ts time.Time, tokenId uint32) RedisKey {
	return RedisKey{
		ts:      ts.Format(KeyTsFmt),
		tokenId: fmt.Sprintf("%d", tokenId),
		TS:      ts,
		TokenId: tokenId,
	}
}

func NewIdxKey(tokenId uint32) RedisIdxKey {
	return RedisIdxKey{
		tokenId: fmt.Sprintf("%d", tokenId),
		TokenId: tokenId,
	}
}

func (k *RedisKey) GetLTPKey() string {
	return fmt.Sprintf(LtpKeyFmt, k.ts, k.tokenId)
}

func (k *RedisIdxKey) GetLTPIdxKey() string {
	return fmt.Sprintf(LtpIdxKeyFmt, k.tokenId)
}

func (k *RedisKey) GetVOLKey() string {
	return fmt.Sprintf(VolKeyFmt, k.ts, k.tokenId)
}

func (k *RedisIdxKey) GetVOLIdxKey() string {
	return fmt.Sprintf(VolIdxKeyFmt, k.tokenId)
}

func (k *RedisKey) GetCS1MKey() string {
	return fmt.Sprintf(Cs1mKeyFmt, k.ts, k.tokenId)
}

func (k *RedisIdxKey) GetCS1MIdxKey() string {
	return fmt.Sprintf(Cs1mIdxKeyFmt, k.tokenId)
}

func (k *RedisKey) GetCS15MKey() string {
	return fmt.Sprintf(Cs15mKeyFmt, k.ts, k.tokenId)
}

func (k *RedisIdxKey) GetCS15MIdxKey() string {
	return fmt.Sprintf(Cs15mIdxKeyFmt, k.tokenId)
}

func (k *RedisKey) GetScore() float64 {
	ts, _ := time.Parse(KeyTsFmt, k.ts)
	return float64(ts.Unix())
}

func ParseKey(key string) RedisKey {
	arr := strings.Split(key, ":")
	ts, _ := time.Parse(KeyTsFmt, arr[3])
	tid, _ := strconv.ParseInt(arr[4], 10, 64)

	return RedisKey{
		ts:      arr[3],
		tokenId: arr[4],
		TS:      ts,
		TokenId: uint32(tid),
	}
}
