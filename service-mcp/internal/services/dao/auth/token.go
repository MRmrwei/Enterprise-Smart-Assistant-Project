package auth

import "github.com/golang-jwt/jwt/v4"

type GenerateToken interface {
	AccessToken(claims jwt.MapClaims) (string, error)
	RefreshToken(claims jwt.MapClaims) (string, error)
}
