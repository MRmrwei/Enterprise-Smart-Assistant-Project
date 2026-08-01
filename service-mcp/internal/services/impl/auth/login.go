package auth

import (
	"ai/service-mcp/internal/repository/dao/user"
	"ai/service-mcp/internal/services/dao/auth"
	"ai/service-mcp/internal/svc/app"
	"context"
	"errors"
	"github.com/golang-jwt/jwt/v4"
	"gorm.io/gorm"
	"time"
)

type LoginImpl struct {
	app       app.Application
	pwdImpl   auth.Password
	tokenImpl auth.GenerateToken
	userRepo  user.UserDao
}

func NewLoginImpl(app app.Application, pwdImpl auth.Password, tokenImpl auth.GenerateToken, userRepo user.UserDao) auth.Login {
	return &LoginImpl{app: app, pwdImpl: pwdImpl, tokenImpl: tokenImpl, userRepo: userRepo}
}

func (this *LoginImpl) Login(ctx context.Context, account string, password string) (string, error) {

	userModel, err := this.userRepo.GetByAccount(ctx, account)

	if err != nil && errors.Is(err, gorm.ErrRecordNotFound) {
		return "", errors.New("账号不存在！")
	}

	if !this.pwdImpl.Verify(password, userModel.Password) {
		return "", errors.New("密码错误！")
	}

	claims := jwt.MapClaims{
		"name": userModel.Nickname,
		"uid":  userModel.ID,
		"iat":  time.Now().Unix(),
		"exp":  time.Now().Add(time.Duration(this.app.GetConfig().AuthConfig.AccessExpire) * time.Second).Unix(),
	}

	token, err := this.tokenImpl.AccessToken(claims)

	return token, nil
}
