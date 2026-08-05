package app

import (
	"gateway/internal/config"
)

type Configura interface {
	Config() config.Config
}

type Application interface {
	Configura
}
