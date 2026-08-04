package repository

import (
	"ai/service-mcp/internal/repository/models"
	"context"
	"errors"
	"gorm.io/gorm"
)

type UserRepo struct {
	db *gorm.DB
}

func NewUserRepo(db *gorm.DB) *UserRepo {
	return &UserRepo{db: db}
}

func (u *UserRepo) GetByAccount(ctx context.Context, account string) (*models.UserModel, error) {
	var user models.UserModel
	err := u.db.WithContext(ctx).Where("account = ?", account).First(&user).Error
	return &user, err
}

func (u *UserRepo) GetRole(ctx context.Context, uid int64) ([]models.RoleModel, error) {
	var roleIds []int64
	var roles []models.RoleModel

	err := u.db.WithContext(ctx).Model(&models.UserRoleModel{}).Where("user_id = ?", uid).Pluck("role_id", &roleIds).Error

	if err != nil {
		return nil, err
	}

	if len(roleIds) <= 0 {
		return nil, errors.New("用户没有角色")
	}

	err = u.db.WithContext(ctx).Model(&models.RoleModel{}).Where("id in ?", roleIds).Select("name, code").Find(&roles).Error

	if err != nil {
		return nil, err
	}

	if len(roles) <= 0 {
		return nil, errors.New("角色不存在！")
	}

	return roles, nil
}

func (u *UserRepo) InfoByUid(ctx context.Context, uid int64) (*models.UserModel, error) {
	var user models.UserModel
	err := u.db.WithContext(ctx).Where("id = ?", uid).First(&user).Error
	return &user, err
}
