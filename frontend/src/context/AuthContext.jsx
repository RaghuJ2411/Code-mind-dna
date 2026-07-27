import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

const AuthContext = createContext({
  user: null,
  loading: false,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
});


function clearClientSession() {
  // Required clears (spec)
  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  sessionStorage.clear();

  // Explicit cache/localStorage clear (spec)
  try {
    localStorage.clear();
  } catch {
    // ignore
  }

  // Disconnect websockets / other realtime channels (best-effort)
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event('auth:session-cleared'));
    window.dispatchEvent(new Event('auth:logout'));
    window.dispatchEvent(new Event('codemind:cache-disconnect'));
  }
}


export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();


  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }

    api.get('/auth/me')
      .then((response) => setUser(response.data))
      .catch(() => {
        clearClientSession();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = async (payload) => {
    const response = await api.post('/auth/login', payload);
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    setUser(response.data.user);
    return response.data;
  };

  const register = async (payload) => {
    const response = await api.post('/auth/register', payload);
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    setUser(response.data.user);
    return response.data;
  };

  const logout = async (options = {}) => {
    const { redirectToLogin = true } = options;
    try {
      await api.post('/auth/logout');
    } catch {
      // Gracefully continue even if the backend is unavailable.
    } finally {
      clearClientSession();
      setUser(null);
      if (redirectToLogin) {
        navigate('/login', { replace: true });
      }
    }
  };

  const value = useMemo(() => ({ user, loading, login, register, logout }), [user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
