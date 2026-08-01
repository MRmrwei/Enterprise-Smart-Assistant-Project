package auth

import (
	"ai/service-mcp/internal/config"
	"ai/service-mcp/internal/services/dao/auth"
	"github.com/golang-jwt/jwt/v4"
)

type GenerateTokenImpl struct {
	Config config.AuthConfig
}

func NewGenerateTokenImpl(c config.AuthConfig) auth.GenerateToken {
	return &GenerateTokenImpl{Config: c}
}

func (this *GenerateTokenImpl) AccessToken(claims jwt.MapClaims) (string, error) {
	return jwt.NewWithClaims(jwt.SigningMethodHS256, claims).
		SignedString([]byte(this.Config.AccessSecret))
}

func (this *GenerateTokenImpl) RefreshToken(claims jwt.MapClaims) (string, error) {
	return jwt.NewWithClaims(jwt.SigningMethodHS256, claims).
		SignedString([]byte(this.Config.RefreshSecret))
}
