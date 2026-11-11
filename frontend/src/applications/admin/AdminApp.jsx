import { useCallback, useEffect, useMemo, useState } from 'react'
import { adminRequest, apiErrorMessage } from './adminApi'
import { getAdminProfile, changeAdminPassword } from './features/account/services/accountService'
import { getCurrentAdmin, signIn } from './features/auth/services/authService'

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', group: 'Workspace', icon: '▦' },
  { id: 'pois', label: 'POIs', group: 'Manage', icon: '⌖' },
  { id: 'users', label: 'Users', group: 'Manage', icon: '♙' },
  { id: 'roles', label: 'Roles', group: 'Manage', icon: '◇' },
  { id: 'menus', label: 'Menus', group: 'Manage', icon: '≡' },
  { id: 'registrations', label: 'Registrations', group: 'Review', icon: '◷' },
  { id: 'submissions', label: 'Submissions', group: 'Review', icon: '▤' },
  { id: 'account', label: 'Account', group: 'Settings', icon: '⚙' },
]

const POI_FIELDS = [
  { name: 'name', label: 'POI name', required: true },
  { name: 'address', label: 'Address', required: true },
  { name: 'open_at', label: 'Opens at', placeholder: '08:00', required: true },
  { name: 'close_at', label: 'Closes at', placeholder: '17:00', required: true },
  { name: 'contact', label: 'Contact', required: true },
  { name: 'description', label: 'Description', kind: 'textarea' },
  { name: 'image', label: 'Image URL' },
  { name: 'latitude', label: 'Latitude', kind: 'number', step: 'any', required: true },
  { name: 'longitude', label: 'Longitude', kind: 'number', step: 'any', required: true },
  { name: 'trigger_radius', label: 'Trigger radius (m)', kind: 'number', required: true },
]

const USER_FIELDS = [
  { name: 'name', label: 'Full name', required: true },
  { name: 'email', label: 'Email', required: true },
  { name: 'phone', label: 'Phone', required: true },
  { name: 'password', label: 'Password', kind: 'password', requiredOnCreate: true },
  { name: 'role_id', label: 'Role ID', required: true },
  {
    name: 'status',
    label: 'Status',
    kind: 'select',
    options: ['ACTIVE', 'INACTIVE'],
    required: true,
  },
  {
    name: 'is_poi_owner_verified',
    label: 'POI owner verified',
    kind: 'checkbox',
  },
]

const ROLE_FIELDS = [
  { name: 'name', label: 'Role name', required: true },
  {
    name: 'permissions',
    label: 'Permissions',
    kind: 'permissions',
  },
  { name: 'priority', label: 'Priority', kind: 'number', required: true },
]

const PERMISSION_GROUPS = [
  {
    label: 'Points of interest',
    options: ['poi.read', 'poi.create', 'poi.update', 'poi.delete', 'poi.approve', 'poi.toggle'],
  },
  {
    label: 'Menus',
    options: ['menu.read', 'menu.create', 'menu.update', 'menu.delete'],
  },
  {
    label: 'Users',
    options: ['user.read', 'user.create', 'user.update', 'user.delete'],
  },
  {
    label: 'Roles',
    options: ['role.read', 'role.create', 'role.update', 'role.delete'],
  },
  {
    label: 'Owners',
    options: ['owner.register', 'owner.access', 'owner.submit_poi', 'owner.manage_own_poi'],
  },
  {
    label: 'Content',
    options: ['content.moderate', 'content.publish'],
  },
  {
    label: 'Analytics',
    options: ['analytics.view', 'analytics.export', 'analytics.view_own'],
  },
  {
    label: 'Audit',
    options: ['audit.read', 'audit.manage'],
  },
  {
    label: 'System',
    options: ['system.config', 'system.logs', 'system.backup'],
  },
]

const RESOURCE_CONFIG = {
  pois: {
    title: 'Points of interest',
    singular: 'POI',
    path: '/pois',
    fields: POI_FIELDS,
    columns: [
      ['name', 'Name'],
      ['address', 'Address'],
      ['contact', 'Contact'],
      ['open_at', 'Hours', (item) => `${item.open_at}–${item.close_at}`],
    ],
  },
  users: {
    title: 'Users',
    singular: 'user',
    path: '/users',
    fields: USER_FIELDS,
    columns: [
      ['name', 'Name'],
      ['email', 'Email'],
      ['phone', 'Phone'],
      ['status', 'Status'],
    ],
  },
  roles: {
    title: 'Roles',
    singular: 'role',
    path: '/roles',
    fields: ROLE_FIELDS,
    columns: [
      ['name', 'Name'],
      ['priority', 'Priority'],
      ['permissions', 'Permissions', (item) => item.permissions?.length ?? 0],
    ],
  },
}

function getStoredToken() {
  try {
    return window.localStorage.getItem('admin.accessToken') || ''
  } catch {
    return ''
  }
}

function LoginScreen({ onLogin, busy, error }) {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [manualToken, setManualToken] = useState('')
  const [showToken, setShowToken] = useState(false)

  async function submit(event) {
    event.preventDefault()
    await onLogin(identifier, password)
  }

  function useToken(event) {
    event.preventDefault()
    onLogin(null, null, manualToken.trim())
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="brand-mark">D</div>
        <p className="eyebrow">DU LỊCH ẨM THỰC</p>
        <h1>Welcome back</h1>
        <p className="muted">Sign in to manage your admin workspace.</p>
        {error && <Notice tone="error">{error}</Notice>}
        <form className="stack-form" onSubmit={submit}>
          <label>
            Email or phone
            <input
              autoComplete="username"
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          <button className="button button-primary button-wide" disabled={busy}>
            {busy ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
        <button
          className="text-button token-toggle"
          onClick={() => setShowToken((shown) => !shown)}
          type="button"
        >
          {showToken ? 'Hide' : 'Use an existing access token'}
        </button>
        {showToken && (
          <form className="stack-form token-form" onSubmit={useToken}>
            <label>
              Access token
              <textarea
                rows="3"
                value={manualToken}
                onChange={(event) => setManualToken(event.target.value)}
                required
              />
            </label>
            <button className="button button-secondary" disabled={busy}>
              Continue
            </button>
          </form>
        )}
        <p className="auth-footnote">
          Authentication is verified with <code>/admin/auth/me</code>.
        </p>
      </section>
    </main>
  )
}

function AdminApp() {
  const [token, setToken] = useState(getStoredToken)
  const [user, setUser] = useState(null)
  const [authBusy, setAuthBusy] = useState(Boolean(getStoredToken()))
  const [authError, setAuthError] = useState('')
  const [activePage, setActivePage] = useState('overview')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    if (!token) return

    let active = true
    getCurrentAdmin(token)
      .then((currentUser) => {
        if (!active) return
        setUser(currentUser)
        window.localStorage.setItem('admin.accessToken', token)
      })
      .catch((error) => {
        if (!active) return
        setUser(null)
        setToken('')
        window.localStorage.removeItem('admin.accessToken')
        setAuthError(apiErrorMessage(error))
      })
      .finally(() => {
        if (active) setAuthBusy(false)
      })

    return () => {
      active = false
    }
  }, [token])

  async function login(identifier, password, accessToken) {
    setAuthBusy(true)
    setAuthError('')
    try {
      let tokenValue = accessToken
      if (!tokenValue) {
        const result = await signIn(identifier, password)
        tokenValue = result.access_token
      }
      setToken(tokenValue)
    } catch (error) {
      setAuthError(apiErrorMessage(error))
      setAuthBusy(false)
    }
  }

  function logout() {
    window.localStorage.removeItem('admin.accessToken')
    setToken('')
    setUser(null)
    setAuthError('')
    setActivePage('overview')
  }

  if (authBusy) {
    return (
      <main className="auth-page">
        <div className="loading-card">
          <span className="spinner" />
          <span>Checking your session…</span>
        </div>
      </main>
    )
  }

  if (!user || !token) {
    return <LoginScreen onLogin={login} busy={authBusy} error={authError} />
  }

  const currentPage = NAV_ITEMS.find((item) => item.id === activePage)

  return (
    <div className="admin-shell">
      <button
        className="mobile-menu-button"
        type="button"
        onClick={() => setSidebarOpen((open) => !open)}
        aria-label="Toggle navigation"
      >
        ☰
      </button>
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-mark">D</div>
          <div>
            <strong>Hệ thống quản lý du lịch ẩm thực</strong>
            <span>Admin console</span>
          </div>
        </div>
        {['Workspace', 'Manage', 'Review', 'Settings'].map((group) => (
          <div className="nav-group" key={group}>
            <p className="nav-heading">{group}</p>
            {NAV_ITEMS.filter((item) => item.group === group).map((item) => (
              <button
                className={`nav-item ${activePage === item.id ? 'nav-item-active' : ''}`}
                key={item.id}
                onClick={() => {
                  setActivePage(item.id)
                  setSidebarOpen(false)
                }}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </div>
        ))}
        <div className="sidebar-footer">
          <div className="avatar">{initials(user.name || user.email)}</div>
          <div className="sidebar-user">
            <strong>{user.name || user.email || 'Administrator'}</strong>
            <span>Administrator</span>
          </div>
          <button className="icon-button" onClick={logout} title="Sign out">
            ↗
          </button>
        </div>
      </aside>
      {sidebarOpen && (
        <button
          className="sidebar-scrim"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <main className="main-area">
        <header className="topbar">
          <div>
            <p className="eyebrow">ADMINISTRATION</p>
            <h1>{currentPage?.label}</h1>
          </div>
          <div className="topbar-user">
            <span className="online-dot" />
            <span>{user.name || user.email || 'Admin account'}</span>
            <div className="avatar avatar-small">{initials(user.name || user.email)}</div>
          </div>
        </header>
        <section className="page-content">
          {activePage === 'overview' && (
            <Overview onNavigate={setActivePage} user={user} />
          )}
          {RESOURCE_CONFIG[activePage] && (
            <ResourceSection
              key={activePage}
              config={RESOURCE_CONFIG[activePage]}
              token={token}
            />
          )}
          {activePage === 'menus' && <MenuSection token={token} />}
          {activePage === 'registrations' && (
            <ReviewSection
              token={token}
              kind="registrations"
              title="Owner registrations"
              path="/registrations"
              reviewField="status"
            />
          )}
          {activePage === 'submissions' && (
            <ReviewSection
              token={token}
              kind="submissions"
              title="POI submissions"
              path="/poi-submissions"
              reviewField="review_status"
            />
          )}
          {activePage === 'account' && (
            <AccountSection token={token} user={user} />
          )}
        </section>
      </main>
    </div>
  )
}

function Overview({ onNavigate, user }) {
  const cards = [
    { title: 'POI directory', detail: 'Create and maintain places', page: 'pois', icon: '⌖' },
    { title: 'User access', detail: 'Manage users and roles', page: 'users', icon: '♙' },
    { title: 'Menu catalog', detail: 'Edit menus by location', page: 'menus', icon: '≡' },
    { title: 'Review queue', detail: 'Approve registrations and changes', page: 'submissions', icon: '◷' },
  ]

  return (
    <>
      <div className="welcome-panel">
        <div>
          <p className="eyebrow">YOUR WORKSPACE</p>
          <h2>Good to see you, {user.name?.split(' ')[0] || 'Admin'}.</h2>
          <p>Manage places, people, and incoming changes from one place.</p>
        </div>
        <div className="welcome-art" aria-hidden="true">
          <span>✦</span><span>⌖</span><span>✦</span>
        </div>
      </div>
      <div className="section-heading">
        <div>
          <h2>Quick access</h2>
          <p className="muted">Jump into a workspace to get started.</p>
        </div>
      </div>
      <div className="quick-grid">
        {cards.map((card) => (
          <button className="quick-card" key={card.page} onClick={() => onNavigate(card.page)}>
            <span className="quick-icon">{card.icon}</span>
            <span className="quick-card-title">{card.title}</span>
            <span className="quick-card-detail">{card.detail}</span>
            <span className="quick-arrow">↗</span>
          </button>
        ))}
      </div>
    </>
  )
}

function ResourceSection({ config, token }) {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(null)
  const [saving, setSaving] = useState(false)
  const [notice, setNotice] = useState('')

  const loadRecords = useCallback(async () => {
    try {
      setRecords(await adminRequest(config.path, token))
      setError('')
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }, [config.path, token])

  useEffect(() => {
    let active = true
    adminRequest(config.path, token)
      .then((items) => {
        if (active) {
          setRecords(items)
          setError('')
        }
      })
      .catch((requestError) => {
        if (active) setError(apiErrorMessage(requestError))
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [config.path, token])

  async function saveRecord(values) {
    setSaving(true)
    setError('')
    try {
      const isEditing = Boolean(editing?.id)
      await adminRequest(
        isEditing ? `${config.path}/${editing.id}` : config.path,
        token,
        { method: isEditing ? 'PUT' : 'POST', body: values },
      )
      setEditing(null)
      setNotice(`${config.singular} ${isEditing ? 'updated' : 'created'}.`)
      await loadRecords()
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    } finally {
      setSaving(false)
    }
  }

  async function deleteRecord(record) {
    if (!window.confirm(`Delete this ${config.singular}?`)) return
    setLoading(true)
    setError('')
    try {
      await adminRequest(`${config.path}/${record.id}`, token, { method: 'DELETE' })
      setNotice(`${config.singular} deleted.`)
      await loadRecords()
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    }
  }

  return (
    <>
      <div className="section-heading">
        <div>
          <h2>{config.title}</h2>
          <p className="muted">Create, edit, and remove records.</p>
        </div>
        <button
          className="button button-primary"
          onClick={() => {
            setNotice('')
            setEditing({})
          }}
        >
          <span>＋</span> Add {config.singular}
        </button>
      </div>
      {notice && <Notice onClose={() => setNotice('')}>{notice}</Notice>}
      {error && <Notice tone="error">{error}</Notice>}
      {editing && (
        <ResourceForm
          config={config}
          initial={editing}
          busy={saving}
          onCancel={() => setEditing(null)}
          onSave={saveRecord}
        />
      )}
      <div className="table-card">
        <div className="table-toolbar">
          <div><strong>All {config.title.toLowerCase()}</strong><span>{records.length} records</span></div>
          <button className="button button-quiet" onClick={loadRecords}>↻ Refresh</button>
        </div>
        {loading ? <LoadingRow /> : records.length === 0 ? (
          <EmptyState title="Nothing here yet" detail="Add a record to get started." />
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  {config.columns.map(([, label]) => <th key={label}>{label}</th>)}
                  <th className="actions-heading">Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => (
                  <tr key={record.id}>
                    {config.columns.map(([key, , render]) => (
                      <td key={key}>{render ? render(record) : displayValue(record[key])}</td>
                    ))}
                    <td className="row-actions">
                      <button
                        className="text-button"
                        onClick={() => {
                          setNotice('')
                          setEditing(record)
                        }}
                      >
                        Edit
                      </button>
                      <button className="text-button text-danger" onClick={() => deleteRecord(record)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  )
}

function ResourceForm({ config, initial, busy, onCancel, onSave }) {
  const [values, setValues] = useState(() => initialValues(config, initial))
  const editingExisting = Boolean(initial.id)

  function submit(event) {
    event.preventDefault()
    const payload = {}
    for (const field of config.fields) {
      const value = values[field.name]
      if (field.kind === 'checkbox') {
        payload[field.name] = Boolean(value)
      } else if (field.kind === 'number') {
        if (value !== '' && value !== undefined) payload[field.name] = Number(value)
      } else if (field.name === 'permissions') {
        payload[field.name] = Array.isArray(value) ? value : []
      } else if (value !== '' && value !== undefined) {
        payload[field.name] = value
      }
    }
    onSave(payload)
  }

  return (
    <section className="form-card">
      <div className="form-card-heading">
        <div>
          <p className="eyebrow">{editingExisting ? 'EDIT RECORD' : 'NEW RECORD'}</p>
          <h3>{editingExisting ? `Edit ${config.singular}` : `Add ${config.singular}`}</h3>
        </div>
        <button className="icon-button" onClick={onCancel} aria-label="Close form">×</button>
      </div>
      <form className="resource-form" onSubmit={submit}>
        {config.fields.map((field) => {
          if (field.name === 'password' && editingExisting) {
            return (
              <FieldInput
                field={{ ...field, required: false, help: 'Leave blank to keep the current password.' }}
                key={field.name}
                value={values[field.name] ?? ''}
                onChange={(value) => setValues({ ...values, [field.name]: value })}
              />
            )
          }
          return (
            <FieldInput
              field={{ ...field, required: field.required || (!editingExisting && field.requiredOnCreate) }}
              key={field.name}
              value={values[field.name] ?? ''}
              onChange={(value) => setValues({ ...values, [field.name]: value })}
            />
          )
        })}
        <div className="form-actions">
          <button type="button" className="button button-secondary" onClick={onCancel}>Cancel</button>
          <button className="button button-primary" disabled={busy}>{busy ? 'Saving…' : 'Save changes'}</button>
        </div>
      </form>
    </section>
  )
}

function FieldInput({ field, value, onChange }) {
  if (field.kind === 'permissions') {
    const selected = Array.isArray(value) ? value : []
    const allPermissions = PERMISSION_GROUPS.flatMap((group) => group.options)
    const allSelected = selected.length === allPermissions.length

    function togglePermission(permission) {
      onChange(
        selected.includes(permission)
          ? selected.filter((item) => item !== permission)
          : [...selected, permission],
      )
    }

    return (
      <fieldset className="permission-panel">
        <legend>{field.label}</legend>
        <div className="permission-panel-heading">
          <small>Select the actions this role is allowed to perform.</small>
          <div className="permission-panel-actions">
            <span>{selected.length} selected</span>
            <button
              type="button"
              className="text-button"
              onClick={() => onChange(allSelected ? [] : allPermissions)}
            >
              {allSelected ? 'Clear all' : 'Select all'}
            </button>
          </div>
        </div>
        <div className="permission-groups">
          {PERMISSION_GROUPS.map((group) => (
            <section className="permission-group" key={group.label}>
              <h4>{group.label}</h4>
              <div className="permission-options">
                {group.options.map((permission) => (
                  <label className="permission-option" key={permission}>
                    <input
                      type="checkbox"
                      checked={selected.includes(permission)}
                      onChange={() => togglePermission(permission)}
                    />
                    <span>{permission}</span>
                  </label>
                ))}
              </div>
            </section>
          ))}
        </div>
      </fieldset>
    )
  }

  return (
    <label className={`field ${field.kind === 'textarea' ? 'field-wide' : ''} ${field.kind === 'checkbox' ? 'field-checkbox' : ''}`}>
      {field.kind === 'checkbox' ? (
        <>
          <input type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(event.target.checked)} />
          <span>{field.label}</span>
        </>
      ) : (
        <>
          <span>{field.label}{field.required && <b className="required-mark"> *</b>}</span>
          {field.kind === 'textarea' ? (
            <textarea rows="3" value={value ?? ''} onChange={(event) => onChange(event.target.value)} required={field.required} placeholder={field.placeholder} />
          ) : field.kind === 'select' ? (
            <select value={value ?? ''} onChange={(event) => onChange(event.target.value)} required={field.required}>
              {field.options.map((option) => <option key={option}>{option}</option>)}
            </select>
          ) : (
            <input
              type={field.kind === 'number' ? 'number' : field.kind || 'text'}
              step={field.step}
              value={value ?? ''}
              onChange={(event) => onChange(event.target.value)}
              required={field.required}
              placeholder={field.placeholder}
            />
          )}
          {field.help && <small>{field.help}</small>}
        </>
      )}
    </label>
  )
}

function MenuSection({ token }) {
  const [pois, setPois] = useState([])
  const [poiId, setPoiId] = useState('')
  const [records, setRecords] = useState([])
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ name: '', price: '' })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  useEffect(() => {
    adminRequest('/pois', token)
      .then((items) => {
        setPois(items)
        if (items.length) setPoiId(items[0].id)
      })
      .catch((requestError) => setError(apiErrorMessage(requestError)))
  }, [token])

  const loadItems = useCallback(async () => {
    if (!poiId) return
    try {
      setRecords(await adminRequest(`/menu-items/poi/${poiId}`, token))
      setError('')
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }, [poiId, token])

  useEffect(() => {
    if (!poiId) return

    let active = true
    adminRequest(`/menu-items/poi/${poiId}`, token)
      .then((items) => {
        if (active) {
          setRecords(items)
          setError('')
        }
      })
      .catch((requestError) => {
        if (active) setError(apiErrorMessage(requestError))
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [poiId, token])

  async function saveMenuItem(event) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      const isEditing = Boolean(editing)
      await adminRequest(isEditing ? `/menu-items/${editing.id}` : '/menu-items', token, {
        method: isEditing ? 'PUT' : 'POST',
        body: { poi_id: poiId, name: form.name, price: Number(form.price) },
      })
      setEditing(null)
      setForm({ name: '', price: '' })
      setNotice(`Menu item ${isEditing ? 'updated' : 'created'}.`)
      await loadItems()
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    } finally {
      setSaving(false)
    }
  }

  async function deleteItem(item) {
    if (!window.confirm(`Delete "${item.name}"?`)) return
    setLoading(true)
    setError('')
    try {
      await adminRequest(`/menu-items/${item.id}`, token, { method: 'DELETE' })
      setNotice('Menu item deleted.')
      await loadItems()
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    }
  }

  return (
    <>
      <div className="section-heading">
        <div><h2>Menu items</h2><p className="muted">Choose a POI to manage its menu.</p></div>
      </div>
      {error && <Notice tone="error">{error}</Notice>}
      {notice && <Notice onClose={() => setNotice('')}>{notice}</Notice>}
      <div className="filter-card">
        <label className="filter-label">
          Location
          <select value={poiId} onChange={(event) => setPoiId(event.target.value)}>
            {!pois.length && <option value="">No POIs available</option>}
            {pois.map((poi) => <option key={poi.id} value={poi.id}>{poi.name}</option>)}
          </select>
        </label>
        <button
          className="button button-primary"
          disabled={!poiId}
          onClick={() => {
            setEditing(false)
            setForm({ name: '', price: '' })
          }}
        >
          ＋ Add menu item
        </button>
      </div>
      {editing !== null && (
        <section className="form-card compact-form">
          <div className="form-card-heading">
            <div><p className="eyebrow">{editing ? 'EDIT ITEM' : 'NEW ITEM'}</p><h3>{editing ? 'Edit menu item' : 'Add menu item'}</h3></div>
            <button className="icon-button" onClick={() => setEditing(null)}>×</button>
          </div>
          <form className="resource-form" onSubmit={saveMenuItem}>
            <label className="field">
              <span>Item name <b className="required-mark">*</b></span>
              <input required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            </label>
            <label className="field">
              <span>Price <b className="required-mark">*</b></span>
              <input type="number" min="1" required value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} />
            </label>
            <div className="form-actions">
              <button type="button" className="button button-secondary" onClick={() => setEditing(null)}>Cancel</button>
              <button className="button button-primary" disabled={saving}>{saving ? 'Saving…' : 'Save item'}</button>
            </div>
          </form>
        </section>
      )}
      <div className="table-card">
        <div className="table-toolbar">
          <div><strong>Menu catalog</strong><span>{records.length} items</span></div>
          <button className="button button-quiet" onClick={loadItems}>↻ Refresh</button>
        </div>
        {loading ? <LoadingRow /> : records.length === 0 ? (
          <EmptyState title="No menu items" detail="Add the first item for this location." />
        ) : (
          <div className="table-scroll">
            <table>
              <thead><tr><th>Item</th><th>Price</th><th className="actions-heading">Actions</th></tr></thead>
              <tbody>
                {records.map((item) => (
                  <tr key={item.id}>
                    <td className="primary-cell">{item.name}</td>
                    <td>{Number(item.price).toLocaleString()} ₫</td>
                    <td className="row-actions">
                      <button className="text-button" onClick={() => {
                        setEditing(item)
                        setForm({ name: item.name, price: String(item.price) })
                      }}>Edit</button>
                      <button className="text-button text-danger" onClick={() => deleteItem(item)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  )
}

function ReviewSection({ token, title, path, kind, reviewField }) {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [note, setNote] = useState('')
  const [active, setActive] = useState(null)
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    try {
      setRecords(await adminRequest(path, token))
      setError('')
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }, [path, token])

  useEffect(() => {
    let active = true
    adminRequest(path, token)
      .then((items) => {
        if (active) {
          setRecords(items)
          setError('')
        }
      })
      .catch((requestError) => {
        if (active) setError(apiErrorMessage(requestError))
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [path, token])

  async function review(record, outcome) {
    setSaving(true)
    setError('')
    try {
      await adminRequest(`${path}/${record.id}/review`, token, {
        method: 'PUT',
        body: { [reviewField]: outcome, admin_note: note },
      })
      setActive(null)
      setNote('')
      await load()
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    } finally {
      setSaving(false)
    }
  }

  async function remove(record) {
    if (!window.confirm('Delete this record?')) return
    setLoading(true)
    setError('')
    try {
      await adminRequest(`${path}/${record.id}`, token, { method: 'DELETE' })
      setActive(null)
      await load()
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    }
  }

  const pendingCount = useMemo(
    () => records.filter((record) => (record.status || record.review_status) === 'PENDING').length,
    [records],
  )

  return (
    <>
      <div className="section-heading">
        <div>
          <h2>{title}</h2>
          <p className="muted">{pendingCount} pending review{pendingCount === 1 ? '' : 's'}.</p>
        </div>
        <button className="button button-quiet" onClick={load}>↻ Refresh</button>
      </div>
      {error && <Notice tone="error">{error}</Notice>}
      <div className="review-grid">
        <div className="table-card">
          <div className="table-toolbar">
            <div><strong>Review queue</strong><span>{records.length} records</span></div>
          </div>
          {loading ? <LoadingRow /> : records.length === 0 ? (
            <EmptyState title="Queue is clear" detail="New requests will appear here." />
          ) : (
            <div className="review-list">
              {records.map((record) => {
                const state = record.status || record.review_status
                return (
                  <button
                    className={`review-row ${active?.id === record.id ? 'review-row-active' : ''}`}
                    key={record.id}
                    onClick={() => {
                      setActive(record)
                      setNote(record.admin_note || '')
                    }}
                  >
                    <span className="review-row-main">
                      <strong>{kind === 'registrations' ? `Registration ${shortId(record.id)}` : `Submission ${shortId(record.id)}`}</strong>
                      <small>{formatDate(record.submiss_at || record.created_at)} · {shortId(record.submissed_by || record.sender_id)}</small>
                    </span>
                    <StatusBadge status={state} />
                  </button>
                )
              })}
            </div>
          )}
        </div>
        <div className="table-card review-detail">
          {active ? (
            <>
              <div className="detail-heading">
                <div><p className="eyebrow">REQUEST DETAILS</p><h3>{kind === 'registrations' ? 'Registration' : 'Proposed changes'}</h3></div>
                <StatusBadge status={active.status || active.review_status} />
              </div>
              <dl className="detail-meta">
                <div><dt>Request ID</dt><dd>{active.id}</dd></div>
                <div><dt>Submitted by</dt><dd>{active.submissed_by || active.sender_id}</dd></div>
                {active.for_poi && <div><dt>POI</dt><dd>{active.for_poi}</dd></div>}
                {active.reviewer_id && <div><dt>Reviewer</dt><dd>{active.reviewer_id}</dd></div>}
              </dl>
              {active.proposed_change && (
                <div className="proposal-preview">
                  <span className="field-caption">PROPOSED CHANGE</span>
                  <pre>{JSON.stringify(active.proposed_change, null, 2)}</pre>
                </div>
              )}
              <label className="field review-note">
                <span>Admin note</span>
                <textarea rows="3" value={note} onChange={(event) => setNote(event.target.value)} />
              </label>
              {(active.status || active.review_status) === 'PENDING' ? (
                <div className="review-actions">
                  <button className="button button-danger" disabled={saving} onClick={() => review(active, 'REJECTED')}>Reject</button>
                  <button className="button button-primary" disabled={saving} onClick={() => review(active, 'ACCEPTED')}>
                    {saving ? 'Saving…' : 'Approve'}
                  </button>
                </div>
              ) : (
                <button className="button button-secondary" onClick={() => remove(active)}>Delete record</button>
              )}
            </>
          ) : (
            <EmptyState title="Select a request" detail="Choose a row to inspect and review." />
          )}
        </div>
      </div>
    </>
  )
}

function AccountSection({ token, user }) {
  const [profile, setProfile] = useState(user)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [passwords, setPasswords] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  async function refreshProfile() {
    setLoading(true)
    setError('')
    try {
      setProfile(await getAdminProfile(token))
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }

  async function changePassword(event) {
    event.preventDefault()
    setError('')
    setNotice('')
    if (passwords.new_password !== passwords.confirm_password) {
      setError('New password and confirmation do not match.')
      return
    }
    setLoading(true)
    try {
      await changeAdminPassword(
        token,
        passwords.current_password,
        passwords.new_password,
      )
      setPasswords({ current_password: '', new_password: '', confirm_password: '' })
      setNotice('Password changed successfully.')
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="section-heading">
        <div><h2>Account settings</h2><p className="muted">Your profile and sign-in security.</p></div>
        <button className="button button-quiet" onClick={refreshProfile} disabled={loading}>↻ Refresh profile</button>
      </div>
      {error && <Notice tone="error">{error}</Notice>}
      {notice && <Notice>{notice}</Notice>}
      <div className="account-grid">
        <section className="table-card account-card">
          <p className="eyebrow">PROFILE</p>
          <h3>Administrator profile</h3>
          <div className="profile-block">
            <div className="avatar avatar-large">{initials(profile.name || profile.email)}</div>
            <div><strong>{profile.name || 'Administrator'}</strong><span>{profile.email || 'No email available'}</span></div>
          </div>
          <dl className="detail-meta">
            <div><dt>User ID</dt><dd>{profile.id || '—'}</dd></div>
            <div><dt>Role ID</dt><dd>{profile.role_id || '—'}</dd></div>
            <div><dt>Status</dt><dd><StatusBadge status={profile.status || 'ACTIVE'} /></dd></div>
          </dl>
        </section>
        <section className="table-card account-card">
          <p className="eyebrow">SECURITY</p>
          <h3>Change password</h3>
          <form className="stack-form password-form" onSubmit={changePassword}>
            <label>
              Current password
              <input
                type="password"
                autoComplete="current-password"
                required
                value={passwords.current_password}
                onChange={(event) => setPasswords({ ...passwords, current_password: event.target.value })}
              />
            </label>
            <label>
              New password
              <input
                type="password"
                autoComplete="new-password"
                minLength="8"
                required
                value={passwords.new_password}
                onChange={(event) => setPasswords({ ...passwords, new_password: event.target.value })}
              />
            </label>
            <label>
              Confirm new password
              <input
                type="password"
                autoComplete="new-password"
                minLength="8"
                required
                value={passwords.confirm_password}
                onChange={(event) => setPasswords({ ...passwords, confirm_password: event.target.value })}
              />
            </label>
            <button className="button button-primary" disabled={loading}>{loading ? 'Updating…' : 'Update password'}</button>
          </form>
        </section>
      </div>
    </>
  )
}

function Notice({ children, tone, onClose }) {
  return (
    <div className={`notice ${tone === 'error' ? 'notice-error' : ''}`} role="status">
      <span>{tone === 'error' ? '!' : '✓'}</span>
      <p>{children}</p>
      {onClose && <button className="icon-button" onClick={onClose} aria-label="Dismiss">×</button>}
    </div>
  )
}

function StatusBadge({ status }) {
  const normalized = String(status || 'UNKNOWN').toLowerCase()
  return <span className={`status-badge status-${normalized}`}>{status || 'Unknown'}</span>
}

function EmptyState({ title, detail }) {
  return (
    <div className="empty-state">
      <span className="empty-icon">⌁</span>
      <strong>{title}</strong>
      <p>{detail}</p>
    </div>
  )
}

function LoadingRow() {
  return <div className="loading-row"><span className="spinner" /> Loading records…</div>
}

function initialValues(config, record) {
  if (record.id && config.singular === 'POI') {
    return { ...record, latitude: record.latitude ?? '', longitude: record.longitude ?? '' }
  }
  if (record.id && config.singular === 'role') {
    return { ...record, permissions: record.permissions || [] }
  }
  return { ...record }
}

function displayValue(value) {
  if (value === undefined || value === null || value === '') return '—'
  if (Array.isArray(value)) return value.join(', ')
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  return String(value)
}

function shortId(value = '') {
  return value ? `${value.slice(0, 6)}…${value.slice(-4)}` : '—'
}

function initials(value = '') {
  return value
    .split(/[\s@._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('') || 'AD'
}

function formatDate(value) {
  if (!value) return 'Date unavailable'
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? 'Date unavailable'
    : date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

export default AdminApp
