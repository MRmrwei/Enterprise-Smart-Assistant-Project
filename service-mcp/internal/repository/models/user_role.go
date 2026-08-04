package models

type UserRoleModel struct {
	BaseModel
	UserId int64
	RoleId int64
}

func (u *UserRoleModel) TableName() string {
	return "ai_user_role"
}
