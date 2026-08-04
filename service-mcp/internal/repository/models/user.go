package models

type UserModel struct {
	BaseModel
	Password string
	Account  string
	Nickname string
}

func (u *UserModel) TableName() string {
	return "ai_user"
}
