// Code scaffolded by goctl. Safe to edit.
// goctl 1.10.1

package svc

import (
	"gateway/internal/config"
	"gateway/internal/svc/app"
)

type ServiceContext struct {
	config config.Config
}

func (s *ServiceContext) Config() config.Config {
	return s.config
}

func NewServiceContext(c config.Config) app.Application {
	return &ServiceContext{
		config: c,
	}
}
