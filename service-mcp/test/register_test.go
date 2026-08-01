package test

import (
	"ai/service-mcp/internal/services/impl/auth"
	"testing"
)

func TestRegisterUser(t *testing.T) {
	pwdImpl := auth.NewPasswordImpl()

	pwd, _ := pwdImpl.Encrypt("123456")
	t.Log(pwd)
}
