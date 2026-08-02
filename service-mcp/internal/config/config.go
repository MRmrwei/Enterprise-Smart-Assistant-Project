package config

import (
	"github.com/zeromicro/go-zero/rest"
	"github.com/zeromicro/go-zero/zrpc"
)

type Config struct {
	zrpc.RpcServerConf
	AuthConfig AuthConfig
	Mysql      Mysql
	McpConfig  McpConfig
}

type AuthConfig struct {
	AccessSecret  string
	AccessExpire  int
	RefreshSecret string
	RefreshExpire int
}

type Mysql struct {
	DataSource   string
	MaxIdleConns int
	MaxOpenConns int
	LogLevel     int
}

type McpConfig struct {
	rest.RestConf
	McpName string
	Version string
}
