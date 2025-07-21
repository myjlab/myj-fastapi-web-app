const API_HOST = 'http://localhost:8000'

const logout = () => {
  localStorage.removeItem('token')
  location.href = '/login.html'
}

const handleLoginError = () => {
  alert('ログイン情報が確認できませんでした、ログインページに移動します')
  logout()
}

const handleForbiddenError = () => {
  alert('他のユーザーのタスクは閲覧できません')
  throw new Error('他のユーザーのタスクは閲覧できません')
}

const handleOtherError = () => {
  alert('予期せむエラーが発生しました')
  throw new Error('予期せむエラーが発生しました')
}

/**
 * ユーザー新規登録API
 */
const signUpApi = async (data) => {
  const url = `${API_HOST}/user`
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (res.ok) {
    return await res.json()
  } else if (res.status === 400) {
    console.error(res)
    throw new Error('入力されたメールアドレスは既に登録されています')
  } else {
    console.error(res)
    handleOtherError()
  }
}

/**
 * ログインAPI
 */
const loginApi = async (email, password) => {
  const url = `${API_HOST}/token`
  const res = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    // loginの場合のみ、bodyは特別
    body: `username=${email}&password=${password}`,
  })

  if (res.ok) {
    const data = await res.json()
    localStorage.setItem('token', data.access_token)
    return data
  } else if (res.status === 401) {
    console.error(res)
    throw new Error('メールアドレスまたはパスワードが間違っています')
  } else {
    console.error(res)
    handleOtherError()
  }
}

/**
 * ログインユーザー情報取得するAPI
 */
const getMeApi = async () => {
  const url = `${API_HOST}/me`
  const res = await fetch(url, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })

  if (res.ok) {
    return await res.json()
  } else if (res.status === 401) {
    handleLoginError()
  } else {
    console.error(res)
    handleOtherError()
  }
}

/**
 * 全てのタスク取得するAPI
 */
const getAllTasksApi = async () => {
  const url = `${API_HOST}/tasks`
  const res = await fetch(url, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })

  if (res.ok) {
    return await res.json()
  } else if (res.status === 401) {
    handleLoginError()
  } else {
    console.error(res)
    handleOtherError()
  }
}

/**
 * タスクを完了にするAPI
 */
const doneTaskApi = async (taskId) => {
  const url = `${API_HOST}/task/${taskId}/done`
  const res = await fetch(url, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })

  if (res.ok) {
    return await res.json()
  } else if (res.status === 401) {
    handleLoginError()
  } else {
    console.error(res)
    handleOtherError()
  }
}

/**
 * タスクを未完了にするAPI
 */
const undoneTaskApi = async (taskId) => {
  const url = `${API_HOST}/task/${taskId}/done`
  const res = await fetch(url, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })

  if (res.ok) {
    return await res.json()
  } else if (res.status === 401) {
    handleLoginError()
  } else {
    console.error(res)
    handleOtherError()
  }
}

/**
 * ひとつのタスクを取得するAPI
 */
const getTaskDetailApi = async (taskId) => {
  const url = `${API_HOST}/task/${taskId}`
  const res = await fetch(url, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })

  if (res.ok) {
    return await res.json()
  } else if (res.status === 401) {
    handleLoginError()
  } else if (res.status === 403) {
    handleForbiddenError()
  } else {
    console.error(res)
    handleOtherError()
  }
}

/**
 * タスクを作成するAPI
 */
const createTaskApi = async (data) => {
  const url = `${API_HOST}/task`
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(data),
  })

  if (res.ok) {
    return await res.json()
  } else if (res.status === 401) {
    handleLoginError()
  } else {
    console.error(res)
    handleOtherError()
  }
}

/**
 * タスクを更新するAPI
 */
const updateTaskApi = async (taskId, data) => {
  const url = `${API_HOST}/task/${taskId}`
  const res = await fetch(url, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(data),
  })

  if (res.ok) {
    return await res.json()
  } else if (res.status === 401) {
    handleLoginError()
  } else if (res.status === 403) {
    handleForbiddenError()
  } else {
    console.error(res)
    handleOtherError()
  }
}

/**
 * タスクの画像を更新するAPI
 */
const updateTaskImageApi = async (taskId, file) => {
  const url = `${API_HOST}/task/${taskId}/image`
  const formData = new FormData()
  formData.append('image', file)
  const res = await fetch(url, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: formData,
  })

  if (res.ok) {
    return await res.json()
  } else if (res.status === 401) {
    handleLoginError()
  } else if (res.status === 403) {
    handleForbiddenError()
  } else {
    console.error(res)
    handleOtherError()
  }
}

/**
 * タスクを削除するAPI
 */
const deleteTaskApi = async (taskId) => {
  const url = `${API_HOST}/task/${taskId}`
  const res = await fetch(url, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  })

  if (res.ok) {
    return await res.json()
  } else if (res.status === 401) {
    handleLoginError()
  } else if (res.status === 403) {
    handleForbiddenError()
  } else {
    console.error(res)
    handleOtherError()
  }
}
