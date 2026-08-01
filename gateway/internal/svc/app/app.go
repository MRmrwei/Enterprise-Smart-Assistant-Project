package app

import (
	"gateway/internal/config"
	"gateway/pb"
)

type AgentRpc interface {
	Client() pb.AiClient
}

type Configura interface {
	Config() config.Config
}

type Application interface {
	AgentRpc
	Configura
}
