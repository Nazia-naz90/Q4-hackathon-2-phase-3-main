export interface User {
  id: string;
  email: string;
  username: string;
  is_admin: boolean;
}

export interface UserForSignup {
  username: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface SignupResponse {
  id: string;
  email: string;
  username: string;
  is_admin: boolean;
}