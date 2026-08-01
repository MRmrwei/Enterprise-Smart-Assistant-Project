package logic

import (
	"ai/service-mcp/internal/repository"
	"ai/service-mcp/internal/services/impl/auth"
	"context"

	"ai/service-mcp/internal/svc"
	"ai/service-mcp/pb"

	"github.com/zeromicro/go-zero/core/logx"
)

type LoginLogic struct {
	ctx    context.Context
	svcCtx *svc.ServiceContext
	logx.Logger
}

func NewLoginLogic(ctx context.Context, svcCtx *svc.ServiceContext) *LoginLogic {
	return &LoginLogic{
		ctx:    ctx,
		svcCtx: svcCtx,
		Logger: logx.WithContext(ctx),
	}
}

func (l *LoginLogic) Login(in *pb.LoginRequest) (*pb.LoginResponse, error) {

	pwdImpl := auth.NewPasswordImpl()
	tokenImpl := auth.NewGenerateTokenImpl(l.svcCtx.Config.AuthConfig)
	userRepo := repository.NewUserRepo(l.svcCtx.DB())
	loginImpl := auth.NewLoginImpl(l.svcCtx, pwdImpl, tokenImpl, userRepo)
	token, err := loginImpl.Login(l.ctx, in.Account, in.Password)

	message := ""
	status := pb.STATUS_SUCCESS
	if err != nil {
		message = err.Error()
		status = pb.STATUS_FAIL
	}

	return &pb.LoginResponse{
		Response: &pb.Response{
			Status:  status,
			Message: message,
		},
		Token: token,
	}, nil

}
