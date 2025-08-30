# 🚀 BFF to Backend-Only Authentication Migration Plan

## **Executive Summary**

This comprehensive plan migrates from Backend-for-Frontend (BFF) pattern to traditional frontend/backend separation with production-grade HTTP-only cookie authentication. The plan follows industry best practices and ensures zero downtime migration.

### **Migration Overview**
- **Current**: Single server (port 8000) serving both API and frontend
- **Target**: Separate frontend (port 3000) and backend (port 8000) with cross-origin authentication
- **Timeline**: 8-10 hours (can be done incrementally)
- **Risk Level**: LOW (with comprehensive testing)

---

## **📋 Pre-Migration Requirements**

### **Environment Setup**
- ✅ Node.js 18+ (Next.js compatibility)
- ✅ Python 3.12+ (FastAPI compatibility)
- ✅ Modern browser (Chrome 80+, Firefox 79+, Safari 13+)
- ✅ Git for version control
- ✅ VS Code with extensions (optional but recommended)

### **Configuration Decisions (Based on Your Choices)**
- **Dev Servers**: Manual separate terminals (flexibility)
- **Frontend Port**: 3000 (Next.js default)
- **OAuth Flow**: Backend sets cookie + redirects to frontend
- **Error Handling**: Backend redirects + Frontend error boundaries
- **Environment**: Separate .env files
- **CORS**: Environment-dependent (permissive dev, strict prod)
- **Session**: Refresh token pattern + Silent refresh (industry standard UX)
- **Testing**: Unit tests + Integration tests
- **Legacy Cleanup**: Complete removal of BFF artifacts

---

## **🗺️ Migration Phases**

### **Phase 1: Backend Configuration (3-4 hours)**
- Remove BFF static serving
- Update CORS settings
- Configure cross-origin cookies
- Update OAuth redirect handling
- Implement refresh token pattern
- Update existing tests

### **Phase 2: Frontend Configuration (2-3 hours)**
- Update API client configuration
- Configure development server
- Update authentication flow
- Implement silent token refresh
- Remove BFF-specific code

### **Phase 3: Development Environment (1 hour)**
- Create development scripts
- Update environment variables
- Configure VS Code tasks (optional)

### **Phase 4: Testing & Validation (2-3 hours)**
- Update existing test suites
- Run integration tests
- Manual testing verification
- Performance validation

---

## **🔧 Detailed Implementation Plan**

### **PHASE 1: BACKEND CONFIGURATION**

#### **1.1 Remove BFF Static Serving**

**File**: `backend/app/main.py`
**Action**: Complete removal of Next.js serving logic

```python
# REMOVE ENTIRELY (lines 101-176):
# - frontend_build_path logic
# - StaticFiles mounting
# - SPA catch-all routes
# - Frontend serving endpoints

# KEEP ONLY:
# - API routes
# - Authentication endpoints
# - CORS middleware
# - Health endpoints
```

**Verification Checkpoint**: ✅ Backend starts without frontend dependencies

#### **1.2 Update CORS Configuration**

**File**: `backend/app/core/config.py`

```python
# UPDATE:
ALLOWED_ORIGINS: str = Field(
    default="http://localhost:3000,http://localhost:3001",
    description="Frontend origins for development"
)

# ADD for production:
PRODUCTION_ORIGINS: str = Field(
    default="https://yourdomain.com,https://www.yourdomain.com",
    description="Production frontend origins"
)
```

**File**: `backend/app/main.py`

```python
# UPDATE CORS middleware:
def get_cors_origins():
    if settings.ENVIRONMENT == "production":
        return settings.PRODUCTION_ORIGINS.split(",")
    return settings.ALLOWED_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,  # CRITICAL for cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

**Verification Checkpoint**: ✅ CORS allows localhost:3000 with credentials

#### **1.3 Configure Cross-Origin Cookie Settings**

**File**: `backend/app/core/config.py`

```python
# UPDATE Cookie Configuration:
COOKIE_SECURE: bool = Field(
    default_factory=lambda: os.getenv("ENVIRONMENT", "development") == "production",
    description="Secure cookies for HTTPS (false for localhost dev)"
)

COOKIE_SAMESITE: str = Field(
    default="lax",  # Perfect for cross-origin
    description="SameSite=Lax for cross-origin compatibility"
)

COOKIE_DOMAIN: Optional[str] = Field(
    default=None,  # No domain for localhost
    description="Cookie domain (None for localhost, .yourdomain.com for prod)"
)

# ADD refresh token settings:
REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
    default=30,
    description="Refresh token expiration (30 days for great UX)"
)
```

**Verification Checkpoint**: ✅ Cookie settings configured for cross-origin

#### **1.4 Implement Refresh Token Pattern**

**File**: `backend/app/core/jwt.py`

```python
# ADD to existing JWTManager:
@staticmethod
def create_refresh_token(user_id: str, device_fingerprint: str = None) -> str:
    """Create refresh token for long-term authentication"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
        "fingerprint": device_fingerprint or "default"
    }
    
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

@staticmethod
def refresh_access_token(refresh_token: str) -> dict:
    """Exchange refresh token for new access token"""
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")
            
        user_id = payload.get("sub")
        if not user_id:
            raise JWTError("Token missing user ID")
            
        # Create new access token
        new_access_token = JWTManager.create_access_token(user_id)
        new_refresh_token = JWTManager.create_refresh_token(user_id, payload.get("fingerprint"))
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

**Verification Checkpoint**: ✅ Refresh token functionality implemented

#### **1.5 Update Authentication Endpoints**

**File**: `backend/app/api/v1/auth.py`

```python
# ADD refresh endpoint:
@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token from cookie"""
    try:
        # Get refresh token from cookie
        refresh_token = request.cookies.get(f"{settings.SESSION_COOKIE_NAME}_refresh")
        
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token")
            
        # Exchange for new tokens
        tokens = JWTManager.refresh_access_token(refresh_token)
        
        # Set new cookies
        set_session_cookie(response, tokens["access_token"])
        set_refresh_cookie(response, tokens["refresh_token"])
        
        return {"message": "Token refreshed successfully"}
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        clear_session_cookie(response)
        clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="Token refresh failed")

# ADD new cookie functions:
def set_refresh_cookie(response: Response, refresh_token: str):
    """Set refresh token cookie"""
    cookie_settings = {
        "key": f"{settings.SESSION_COOKIE_NAME}_refresh",
        "value": refresh_token,
        "max_age": settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "path": "/"
    }
    
    if settings.COOKIE_DOMAIN:
        cookie_settings["domain"] = settings.COOKIE_DOMAIN
        
    response.set_cookie(**cookie_settings)

def clear_refresh_cookie(response: Response):
    """Clear refresh token cookie"""
    cookie_settings = {
        "key": f"{settings.SESSION_COOKIE_NAME}_refresh",
        "value": "",
        "max_age": 0,
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "path": "/"
    }
    
    if settings.COOKIE_DOMAIN:
        cookie_settings["domain"] = settings.COOKIE_DOMAIN
        
    response.set_cookie(**cookie_settings)

# UPDATE existing login success handler:
# In oauth_callback function, ADD after setting session cookie:
refresh_token = JWTManager.create_refresh_token(
    user_id=str(user.user_id),
    device_fingerprint=get_client_ip(request)
)
set_refresh_cookie(response, refresh_token)
```

**Verification Checkpoint**: ✅ Refresh token endpoints working

#### **1.6 Update OAuth Callback Redirect**

**File**: `backend/app/api/v1/auth.py`

```python
# UPDATE oauth callback redirect:
# Replace current redirect logic with:

# Determine redirect URL based on success/failure
if return_url and _is_safe_return_url(return_url):
    redirect_url = return_url
else:
    # Default to frontend URL
    redirect_url = f"{settings.FRONTEND_URL}/dashboard"

# Add success parameters
redirect_url += "?auth_success=true&auth_timestamp=" + str(int(datetime.now().timestamp()))

redirect_response = RedirectResponse(url=redirect_url, status_code=302)
```

**Verification Checkpoint**: ✅ OAuth redirects to frontend correctly

#### **1.7 Update Test Fixtures**

**File**: `backend/tests/fixtures/auth_fixtures.py`

```python
# ADD refresh token fixtures:
@pytest.fixture
def refresh_token(sample_user):
    """Generate a valid refresh token for testing."""
    return JWTManager.create_refresh_token(str(sample_user.user_id))

@pytest.fixture
def expired_refresh_token(sample_user):
    """Generate an expired refresh token for testing."""
    # Create token that expired 1 day ago
    expire = datetime.utcnow() - timedelta(days=1)
    to_encode = {
        "sub": str(sample_user.user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow() - timedelta(days=31)
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

@pytest.fixture
def cors_headers():
    """Headers for cross-origin requests"""
    return {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
```

### **PHASE 2: FRONTEND CONFIGURATION**

#### **2.1 Update API Client Configuration**

**File**: `frontend/website/lib/api/client.ts`

```typescript
// UPDATE API base URL:
const API_BASE_URL = (() => {
  const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    new URL(url);
    return url.replace(/\/$/, '');
  } catch {
    console.error('Invalid API_BASE_URL, falling back to localhost:8000');
    return 'http://localhost:8000';
  }
})();

// ADD automatic token refresh interceptor:
class APIClient {
  private isRefreshing = false;
  private refreshPromise: Promise<void> | null = null;

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    let response = await this.makeRequest(endpoint, options);
    
    // If 401 and we haven't tried refreshing, attempt refresh
    if (response.status === 401 && !this.isRefreshing) {
      await this.handleTokenRefresh();
      response = await this.makeRequest(endpoint, options);
    }
    
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    
    return response.json();
  }

  private async makeRequest(endpoint: string, options: RequestInit): Promise<Response> {
    return fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      credentials: 'include', // Critical for cookies
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
  }

  private async handleTokenRefresh(): Promise<void> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.isRefreshing = true;
    this.refreshPromise = this.performRefresh();

    try {
      await this.refreshPromise;
    } finally {
      this.isRefreshing = false;
      this.refreshPromise = null;
    }
  }

  private async performRefresh(): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        // Refresh failed, redirect to login
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        throw new Error('Token refresh failed');
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      throw error;
    }
  }
}

export const apiClient = new APIClient();
```

**Verification Checkpoint**: ✅ API client configured for cross-origin with auto-refresh

#### **2.2 Update Session Management**

**File**: `frontend/website/lib/auth/session.ts`

```typescript
// UPDATE for cross-origin:
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// UPDATE session validation:
export async function getSessionStatus(forceRefresh = false): Promise<SessionStatus> {
  // Check cache first
  if (!forceRefresh && sessionCache.data && Date.now() - sessionCache.timestamp < sessionCache.ttl) {
    return sessionCache.data;
  }

  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/auth/session`, {
      method: 'GET',
      credentials: 'include', // Critical for cross-origin cookies
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 401) {
      // Try token refresh before giving up
      const refreshResponse = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      });

      if (refreshResponse.ok) {
        // Retry original request
        return getSessionStatus(true);
      }
    }

    if (!response.ok) {
      throw new AuthError(AuthErrorType.UNAUTHORIZED, 'Session validation failed');
    }

    const data = await response.json();
    
    const sessionStatus: SessionStatus = {
      isAuthenticated: data.authenticated || false,
      user: data.authenticated ? data.user : null,
      loading: false,
    };

    // Cache the result
    sessionCache.data = sessionStatus;
    sessionCache.timestamp = Date.now();

    return sessionStatus;

  } catch (error) {
    console.error('Session validation error:', error);
    
    const errorStatus: SessionStatus = {
      isAuthenticated: false,
      user: null,
      loading: false,
      error: error instanceof AuthError ? error.message : 'Session validation failed',
    };

    sessionCache.data = errorStatus;
    sessionCache.timestamp = Date.now();

    return errorStatus;
  }
}
```

**Verification Checkpoint**: ✅ Session management working cross-origin

#### **2.3 Update Middleware**

**File**: `frontend/website/middleware.ts`

```typescript
// UPDATE for cross-origin API calls:
async function validateSession(request: NextRequest): Promise<boolean> {
  try {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Forward cookies from the request
    const cookieHeader = request.headers.get('cookie') || '';
    
    const response = await fetchWithTimeout(`${apiBaseUrl}/api/v1/auth/session`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': cookieHeader, // Forward cookies
      },
      cache: 'no-cache',
    });

    if (response.ok) {
      const data = await response.json();
      return data.authenticated === true;
    }

    return false;
  } catch (error) {
    console.error('Middleware session validation error:', error);
    return false;
  }
}
```

**Verification Checkpoint**: ✅ Middleware validates sessions cross-origin

#### **2.4 Update Package.json Scripts**

**File**: `frontend/website/package.json`

```json
{
  "scripts": {
    "dev": "next dev -p 3000",
    "dev:3001": "next dev -p 3001",
    "build": "next build",
    "start": "next start -p 3000",
    "lint": "next lint",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage"
  }
}
```

#### **2.5 Remove BFF-Specific Code**

**File**: `frontend/website/next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Standard Next.js configuration
  images: {
    unoptimized: true,
    remotePatterns: [
      // Keep existing Google CDN patterns
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
        port: '',
        pathname: '/**',
      },
      // ... other existing patterns
    ],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    formats: ['image/webp', 'image/avif'],
  },
  
  trailingSlash: false,
  
  // Standard webpack configuration
  webpack: (config, { isServer }) => {
    // Standard optimizations only
    config.watchOptions = {
      ...config.watchOptions,
      ignored: /node_modules/,
      poll: process.platform === 'win32' ? 1000 : false,
    };
    
    return config;
  },
}

module.exports = nextConfig
```

### **PHASE 3: DEVELOPMENT ENVIRONMENT**

#### **3.1 Create Development Scripts**

**File**: `dev-backend.ps1`

```powershell
# Backend Development Server
Write-Host "🚀 Starting Backend Development Server" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
$backendPath = Join-Path $PSScriptRoot "backend"

Set-Location $backendPath

Write-Host "📍 Backend Directory: $backendPath" -ForegroundColor Blue
Write-Host "🌐 Backend will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "📖 API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "🏥 Health Check: http://localhost:8000/health" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the backend server" -ForegroundColor Gray
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**File**: `dev-frontend.ps1`

```powershell
# Frontend Development Server
Write-Host "🎨 Starting Frontend Development Server" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
$frontendPath = Join-Path $PSScriptRoot "frontend\website"

Set-Location $frontendPath

Write-Host "📍 Frontend Directory: $frontendPath" -ForegroundColor Blue
Write-Host "🌐 Frontend will be available at: http://localhost:3000" -ForegroundColor Green
Write-Host "🔗 API Backend: http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the frontend server" -ForegroundColor Gray
Write-Host ""

npm run dev
```

**File**: `dev-all.ps1`

```powershell
# Start Both Development Servers
Write-Host "🚀 Starting Full Development Environment" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-Command", "& '.\dev-backend.ps1'"

Write-Host "Waiting 3 seconds for backend to initialize..." -ForegroundColor Blue
Start-Sleep 3

Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-Command", "& '.\dev-frontend.ps1'"

Write-Host ""
Write-Host "✅ Both servers started!" -ForegroundColor Green
Write-Host "🎨 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🚀 Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Close terminal windows to stop servers" -ForegroundColor Gray
```

#### **3.2 Environment Variables**

**File**: `frontend/website/.env.local`

```bash
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AI Reddit
NEXT_PUBLIC_ENVIRONMENT=development
```

**File**: `backend/.env`

```bash
# Backend Environment Variables
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
PRODUCTION_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Cookie Settings
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
COOKIE_DOMAIN=

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
SESSION_TOKEN_EXPIRE_HOURS=24
SESSION_COOKIE_NAME=ai_social_session

# Database (keep existing)
DATABASE_URL=sqlite:///./ai_social.db

# Google OAuth (keep existing)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# AI Configuration (keep existing)
GOOGLE_GEMINI_API_KEY=your-gemini-api-key
```

### **PHASE 4: TESTING & VALIDATION**

#### **4.1 Update Authentication Tests**

**File**: `backend/tests/unit/dependencies/test_auth_dependencies.py`

```python
# ADD tests for refresh token functionality:
class TestRefreshTokens:
    """Test refresh token functionality"""
    
    def test_create_refresh_token(self, sample_user):
        """Test refresh token creation"""
        refresh_token = JWTManager.create_refresh_token(str(sample_user.user_id))
        
        # Decode to verify structure
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert payload["sub"] == str(sample_user.user_id)
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_refresh_access_token_success(self, sample_user):
        """Test successful token refresh"""
        refresh_token = JWTManager.create_refresh_token(str(sample_user.user_id))
        
        tokens = JWTManager.refresh_access_token(refresh_token)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
    
    def test_refresh_token_invalid_type(self):
        """Test refresh with invalid token type"""
        # Create access token instead of refresh token
        access_token = JWTManager.create_access_token("test-user-id")
        
        with pytest.raises(HTTPException) as exc_info:
            JWTManager.refresh_access_token(access_token)
        
        assert exc_info.value.status_code == 401
```

#### **4.2 Add CORS Integration Tests**

**File**: `backend/tests/integration/test_cors_auth.py`

```python
"""
Test CORS and Cross-Origin Authentication

Validates that authentication works properly across origins.
"""

import pytest
from fastapi.testclient import TestClient


class TestCORSAuthentication:
    """Test cross-origin authentication scenarios"""
    
    def test_cors_preflight_auth_endpoint(self, client: TestClient):
        """Test CORS preflight for auth endpoints"""
        response = client.options(
            "/api/v1/auth/session",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )
        
        assert response.status_code == 200
        assert "http://localhost:3000" in response.headers.get("Access-Control-Allow-Origin", "")
        assert response.headers.get("Access-Control-Allow-Credentials") == "true"
    
    def test_cross_origin_session_validation(self, client: TestClient, authenticated_user):
        """Test session validation from different origin"""
        response = client.get(
            "/api/v1/auth/session",
            headers={"Origin": "http://localhost:3000"},
            cookies={"ai_social_session": authenticated_user["session_token"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
    
    def test_refresh_token_cross_origin(self, client: TestClient, authenticated_user):
        """Test token refresh from different origin"""
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Origin": "http://localhost:3000"},
            cookies={
                "ai_social_session": authenticated_user["session_token"],
                "ai_social_session_refresh": authenticated_user["refresh_token"]
            }
        )
        
        assert response.status_code == 200
```

#### **4.3 Manual Testing Checklist**

Create comprehensive manual testing procedures:

**File**: `TESTING_CHECKLIST.md`

```markdown
# Manual Testing Checklist

## Pre-Testing Setup
- [ ] Backend server running on http://localhost:8000
- [ ] Frontend server running on http://localhost:3000
- [ ] Browser developer tools open (Network + Application tabs)
- [ ] Clear all cookies and local storage

## Authentication Flow Tests

### Login Process
- [ ] Navigate to http://localhost:3000
- [ ] Click "Login with Google"
- [ ] Verify redirect to Google OAuth
- [ ] Complete Google login
- [ ] Verify redirect back to frontend dashboard
- [ ] Check cookies set in Application tab:
  - [ ] `ai_social_session` cookie present
  - [ ] `ai_social_session_refresh` cookie present
  - [ ] Both cookies have `SameSite=Lax`
  - [ ] Both cookies have `HttpOnly=true`

### Session Validation
- [ ] Refresh the page
- [ ] Verify user remains logged in
- [ ] Check Network tab for `/api/v1/auth/session` call
- [ ] Verify cookies sent with request

### Cross-Origin API Calls
- [ ] Navigate to different pages
- [ ] Verify API calls include cookies
- [ ] Check for CORS headers in responses
- [ ] Verify no CORS errors in console

### Token Refresh
- [ ] Wait for access token to expire (or manually trigger)
- [ ] Make an API call
- [ ] Verify automatic token refresh
- [ ] Check for new cookies in Application tab

### Logout Process
- [ ] Click logout button
- [ ] Verify redirect to login page
- [ ] Check that cookies are cleared
- [ ] Verify subsequent API calls fail appropriately

## Error Scenarios

### Network Errors
- [ ] Disconnect backend server
- [ ] Verify frontend shows appropriate error messages
- [ ] Reconnect backend
- [ ] Verify automatic recovery

### Invalid Sessions
- [ ] Manually corrupt session cookie
- [ ] Verify automatic logout
- [ ] Verify redirect to login page

## Browser Compatibility
- [ ] Test in Chrome
- [ ] Test in Firefox
- [ ] Test in Safari (if available)
- [ ] Test in Edge

## Performance Checks
- [ ] Verify no excessive API calls
- [ ] Check for memory leaks in dev tools
- [ ] Verify reasonable page load times
```

---

## **🎯 Migration Execution Steps**

### **Step 1: Backup Current State**
```bash
git checkout -b backup-bff-auth
git add .
git commit -m "Backup: BFF authentication state before migration"
git checkout dev
git checkout -b migrate-to-backend-only-auth
```

### **Step 2: Execute Backend Changes** (3-4 hours)
1. Update `backend/app/main.py` (remove BFF serving)
2. Update `backend/app/core/config.py` (CORS + cookies)
3. Update `backend/app/core/jwt.py` (refresh tokens)
4. Update `backend/app/api/v1/auth.py` (refresh endpoint)
5. Update test fixtures
6. Run backend tests: `cd backend && python -m pytest`

**Verification**: Backend starts and serves API only

### **Step 3: Execute Frontend Changes** (2-3 hours)
1. Update `frontend/website/lib/api/client.ts`
2. Update `frontend/website/lib/auth/session.ts`
3. Update `frontend/website/middleware.ts`
4. Update `frontend/website/package.json`
5. Update `frontend/website/next.config.js`
6. Update environment variables

**Verification**: Frontend starts on port 3000

### **Step 4: Create Development Scripts** (1 hour)
1. Create `dev-backend.ps1`
2. Create `dev-frontend.ps1`
3. Create `dev-all.ps1`
4. Test all scripts work correctly

**Verification**: Both servers start independently

### **Step 5: Integration Testing** (2-3 hours)
1. Run updated backend tests
2. Manual testing using checklist
3. Performance validation
4. Browser compatibility testing

**Verification**: All tests pass, manual testing successful

### **Step 6: Clean Up Legacy Code** (1 hour)
1. Remove old BFF-related files
2. Clean up unused imports
3. Update documentation
4. Final commit

---

## **🚨 Rollback Plan**

If issues arise during migration:

```bash
# Quick rollback to working BFF state
git checkout backup-bff-auth
npm run dev # Start old BFF system
```

## **🔄 Post-Migration Tasks**

1. **Update Documentation**
   - Update README with new dev setup
   - Document new authentication flow
   - Update deployment guides

2. **Production Preparation**
   - Update production environment variables
   - Configure production CORS origins
   - Test with HTTPS in staging

3. **Monitoring Setup**
   - Add authentication metrics
   - Monitor token refresh rates
   - Track CORS-related errors

---

## **📞 Support & Verification Points**

Throughout the migration, these are key verification points where you should confirm functionality:

1. ✅ **Backend Only**: Backend serves API without frontend
2. ✅ **CORS Working**: Cross-origin requests succeed
3. ✅ **Cookies Set**: Authentication cookies set correctly
4. ✅ **Token Refresh**: Automatic token refresh working
5. ✅ **OAuth Flow**: Complete login/logout cycle works
6. ✅ **Tests Pass**: All automated tests pass
7. ✅ **Manual Testing**: Complete testing checklist

**Ready to begin? Please confirm and I'll guide you through each phase step by step.**
