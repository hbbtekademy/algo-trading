package redistypes

import (
	"fmt"
	"strconv"
	"strings"
	"time"
)

const (
	REDIS_LTP_KEY_PREFIX = "LTP:ts:sym:"
	REDIS_LTP_KEY_FMT    = REDIS_LTP_KEY_PREFIX + "%s:%s"

	REDIS_LTP_IDX_KEY_PREFIX = "IDX:LTP:sym:"
	REDIS_LTP_IDX_KEY_FMT    = REDIS_LTP_IDX_KEY_PREFIX + "%s"

	REDIS_VOL_KEY_PREFIX = "VOL:ts:sym:"
	REDIS_VOL_KEY_FMT    = REDIS_VOL_KEY_PREFIX + "%s:%s"

	REDIS_VOL_IDX_KEY_PREFIX = "IDX:VOL:sym:"
	REDIS_VOL_IDX_KEY_FMT    = REDIS_VOL_IDX_KEY_PREFIX + "%s"

	REDIS_CS1M_KEY_PREFIX = "CS1M:ts:sym:"
	REDIS_CS1M_KEY_FMT    = REDIS_CS1M_KEY_PREFIX + "%s:%s"

	REDIS_CS1M_IDX_KEY_PREFIX = "IDX:CS1M:sym:"
	REDIS_CS1M_IDX_KEY_FMT    = REDIS_CS1M_IDX_KEY_PREFIX + "%s"

	REDIS_CS15M_KEY_PREFIX = "CS15M:ts:sym:"
	REDIS_CS15M_KEY_FMT    = REDIS_CS15M_KEY_PREFIX + "%s:%s"

	REDIS_CS15M_IDX_KEY_PREFIX = "IDX:CS15M:sym:"
	REDIS_CS15M_IDX_KEY_FMT    = REDIS_CS15M_IDX_KEY_PREFIX + "%s"

	REDIS_KEY_TS_FMT = "200601021504"
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
		ts:      ts.Format(REDIS_KEY_TS_FMT),
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
	return fmt.Sprintf(REDIS_LTP_KEY_FMT, k.ts, k.tokenId)
}

func (k *RedisIdxKey) GetLTPIdxKey() string {
	return fmt.Sprintf(REDIS_LTP_IDX_KEY_FMT, k.tokenId)
}

func (k *RedisKey) GetVOLKey() string {
	return fmt.Sprintf(REDIS_VOL_KEY_FMT, k.ts, k.tokenId)
}

func (k *RedisIdxKey) GetVOLIdxKey() string {
	return fmt.Sprintf(REDIS_VOL_IDX_KEY_FMT, k.tokenId)
}

func (k *RedisKey) GetCS1MKey() string {
	return fmt.Sprintf(REDIS_CS1M_KEY_FMT, k.ts, k.tokenId)
}

func (k *RedisIdxKey) GetCS1MIdxKey() string {
	return fmt.Sprintf(REDIS_CS1M_IDX_KEY_FMT, k.tokenId)
}

func (k *RedisKey) GetCS15MKey() string {
	return fmt.Sprintf(REDIS_CS15M_KEY_FMT, k.ts, k.tokenId)
}

func (k *RedisIdxKey) GetCS15MIdxKey() string {
	return fmt.Sprintf(REDIS_CS15M_IDX_KEY_FMT, k.tokenId)
}

func (k *RedisKey) GetScore() float64 {
	ts, _ := time.Parse(REDIS_KEY_TS_FMT, k.ts)
	return float64(ts.Unix())
}

func ParseKey(key string) RedisKey {
	arr := strings.Split(key, ":")
	ts, _ := time.Parse(REDIS_KEY_TS_FMT, arr[3])
	tid, _ := strconv.ParseInt(arr[4], 10, 64)

	return RedisKey{
		ts:      arr[3],
		tokenId: arr[4],
		TS:      ts,
		TokenId: uint32(tid),
	}
}

func ParseIdxKey(key string) RedisIdxKey {
	arr := strings.Split(key, ":")
	tid, _ := strconv.ParseInt(arr[3], 10, 64)

	return RedisIdxKey{
		tokenId: arr[3],
		TokenId: uint32(tid),
	}
}
