const API_HOST = 'http://localhost:8000'

const checkLogin = () => {
  if (localStorage.getItem('token')) {
    return true
  }
  return false
}

const logout = () => {
  localStorage.removeItem('token')
  location.href = '/login.html'
}

const handleLoginError = () => {
  alert('ログイン情報が確認できませんでした、ログインページに移動します')
  logout()
}
