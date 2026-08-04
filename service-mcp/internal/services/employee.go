package services

import (
	"ai/service-mcp/internal/repository"
	"ai/service-mcp/internal/tools/types"
	"context"
	"errors"
	"github.com/zeromicro/go-zero/core/logx"
	"gorm.io/gorm"
)

type EmployeeService struct {
	db *gorm.DB
}

func NewEmployeeService(db *gorm.DB) *EmployeeService {
	return &EmployeeService{
		db: db,
	}
}

func (s *EmployeeService) Info(ctx context.Context, uid int64) (*types.EmployeeInfoResponse, error) {
	user, err := repository.NewUserRepo(s.db).InfoByUid(ctx, uid)

	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("用户不存在")
		}
		return nil, err
	}
	logx.Debug("用户ID = ", uid)
	roles, roleErr := repository.NewUserRepo(s.db).GetRole(ctx, uid)

	if roleErr != nil {
		if errors.Is(roleErr, gorm.ErrRecordNotFound) {
			return nil, errors.New("用户角色不存在")
		}
		return nil, roleErr
	}

	roleNames := make([]string, len(roles))
	roleCodes := make([]string, len(roles))

	for i, role := range roles {
		roleNames[i] = role.Name
		roleCodes[i] = role.Code
	}

	return &types.EmployeeInfoResponse{
		Uid:       int64(user.ID),
		Name:      user.Nickname,
		RoleNames: roleNames,
		RoleCodes: roleCodes,
	}, nil

}
