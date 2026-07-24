// Code scaffolded by goctl. Safe to edit.
// goctl 1.10.1

package svc

import (
	"gateway/internal/config"
)

type ServiceContext struct {
	Config config.Config
}

func NewServiceContext(c config.Config) *ServiceContext {
	return &ServiceContext{
		Config: c,
	}
}
