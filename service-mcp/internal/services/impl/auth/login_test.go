package auth

import (
	"ai/service-mcp/internal/config"
	"ai/service-mcp/internal/repository/models"
	"ai/service-mcp/internal/services/dao/auth"
	"ai/service-mcp/internal/svc/app"
	"context"
	"gorm.io/gorm"
	"testing"
)

func getNewPasswordImpl() auth.Password {
	return NewPasswordImpl()
}

func GetApp() app.Application {
	return application{}
}

type application struct{}

func (a application) GetConfig() config.Config {
	return config.Config{
		AuthConfig: config.AuthConfig{
			AccessSecret: "dddddddddddddwwwww",
			AccessExpire: 86400,
		},
	}
}

func (a application) DB() *gorm.DB {
	return nil
}

type userrepo struct {
}

func (this *userrepo) GetByAccount(ctx context.Context, account string) (*models.UserModel, error) {
	return &models.UserModel{
		Account:  "admin",
		Password: "$2a$10$R/vzxysdmGZN63gcYQ6xCewDWl5EoUs1DpDJgYxhaNghrhNHA7JTG",
	}, nil
}
func TestLoginImpl_Login(t *testing.T) {
	application := GetApp()
	tokenImpl := NewGenerateTokenImpl(application.GetConfig().AuthConfig)
	LoginImpl := NewLoginImpl(application, getNewPasswordImpl(), tokenImpl, &userrepo{})
	ctx := context.Background()

	token, err := LoginImpl.Login(ctx, "admin", "admin")
	t.Log(token, err)

}
