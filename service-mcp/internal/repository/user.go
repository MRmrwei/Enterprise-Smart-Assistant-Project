package repository

import (
	"ai/service-mcp/internal/repository/models"
	"context"
	"gorm.io/gorm"
)

type UserRepo struct {
	db *gorm.DB
}

func NewUserRepo(db *gorm.DB) *UserRepo {
	return &UserRepo{db: db}
}

func (this *UserRepo) GetByAccount(ctx context.Context, account string) (*models.UserModel, error) {
	var user models.UserModel
	err := this.db.WithContext(ctx).Where("account = ?", account).First(&user).Error
	return &user, err
}

func (this *UserRepo) GetRole() {

}
