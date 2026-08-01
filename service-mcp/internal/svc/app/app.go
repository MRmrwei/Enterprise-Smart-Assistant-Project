package app

import (
	"ai/service-mcp/internal/config"
	"gorm.io/gorm"
)

type Application interface {
	GetConfig() config.Config
	DB() *gorm.DB
}
