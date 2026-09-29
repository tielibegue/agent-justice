// Agent-Justice Frontend JavaScript

const API_BASE = '';
const TOKEN_KEY = 'agent_justice_token';

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
}

// Authentification
function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function redirectToLogin() {
    localStorage.removeItem(TOKEN_KEY);
    window.location.href = '/login';
}

async function login(e) {
    e.preventDefault();
    const body = new URLSearchParams({
        username: document.getElementById('login-username').value,
        password: document.getElementById('login-password').value
    });
    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, { method: 'POST', body });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Connexion impossible');
        localStorage.setItem(TOKEN_KEY, data.access_token);
        window.location.href = '/';
    } catch (error) {
        showLoginError(error.message);
    }
}

async function register(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target).entries());
    try {
        const response = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || 'Inscription impossible');
        // Connexion automatique après la création du compte
        document.getElementById('login-username').value = data.username;
        document.getElementById('login-password').value = data.password;
        toggleLoginForm(false);
        document.getElementById('login-form').requestSubmit();
    } catch (error) {
        showLoginError(error.message);
    }
}

function toggleLoginForm(showRegister) {
    event?.preventDefault();
    document.getElementById('login-form').classList.toggle('hidden', showRegister);
    document.getElementById('register-form').classList.toggle('hidden', !showRegister);
    document.getElementById('login-error').classList.add('hidden');
}

function showLoginError(message) {
    const el = document.getElementById('login-error');
    el.textContent = message;
    el.classList.remove('hidden');
}

async function logout() {
    try {
        await apiCall('/api/auth/logout', 'POST');
    } catch (error) {
        console.error(error);
    }
    redirectToLogin();
}

async function loadCurrentUser() {
    const user = await apiCall('/api/auth/me');
    document.getElementById('current-user').textContent = `👤 ${user.username}`;
}

// Navigation
function showSection(sectionName) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(sectionName).classList.add('active');
    event.target.classList.add('active');
    
    // Charger les données de la section
    if (sectionName === 'dashboard') loadDashboard();
    else if (sectionName === 'clients') loadClients();
    else if (sectionName === 'affaires') loadAffaires();
    else if (sectionName === 'echeances') loadEcheances();
    else if (sectionName === 'documents') {
        loadAffairesForFilter();
        loadDocuments();
    }
}

// Dashboard
async function loadDashboard() {
    try {
        const stats = await apiCall('/api/dashboard/');
        
        // Statistiques principales
        document.getElementById('stat-clients').textContent = stats.clients.total;
        document.getElementById('stat-affaires').textContent = stats.affaires.total;
        document.getElementById('stat-echeances').textContent = stats.echeances.total;
        document.getElementById('stat-retard').textContent = stats.echeances.en_retard;
        
        // Affaires par statut
        const affairesParStatut = document.getElementById('affaires-par-statut');
        affairesParStatut.innerHTML = Object.entries(stats.affaires.par_statut).map(([statut, count]) => `
            <div class="statut-item">
                <span>${statut}</span>
                <span class="badge badge-${statut}">${count}</span>
            </div>
        `).join('');
        
        // Échéances proches
        const echeancesProches = document.getElementById('echeances-proches');
        if (stats.echeances_30_jours.length > 0) {
            echeancesProches.innerHTML = stats.echeances_30_jours.map(e => `
                <div class="echeance-item">
                    <h4>${e.titre}</h4>
                    <p>📅 ${new Date(e.date_echeance).toLocaleDateString('fr-FR')}</p>
                </div>
            `).join('');
        } else {
            echeancesProches.innerHTML = '<p style="color: #999; text-align: center;">Aucune échéance à venir</p>';
        }
    } catch (error) {
        console.error('Erreur chargement dashboard:', error);
    }
}

// Modal
async function openModal(type, id = null) {
    const modal = document.getElementById('modal');
    const form = document.getElementById('modal-form');
    const title = document.getElementById('modal-title');
    
    let fields = '';
    
    if (type === 'client') {
        title.textContent = id ? 'Modifier le Client' : 'Nouveau Client';
        fields = `
            <div class="form-group">
                <label for="nom">Nom *</label>
                <input type="text" id="nom" name="nom" required>
            </div>
            <div class="form-group">
                <label for="prenom">Prénom *</label>
                <input type="text" id="prenom" name="prenom" required>
            </div>
            <div class="form-group">
                <label for="email">Email *</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="telephone">Téléphone</label>
                <input type="tel" id="telephone" name="telephone">
            </div>
            <div class="form-group">
                <label for="adresse">Adresse</label>
                <textarea id="adresse" name="adresse" rows="3"></textarea>
            </div>
        `;
    } else if (type === 'affaire') {
        title.textContent = id ? 'Modifier l\'Affaire' : 'Nouvelle Affaire';
        fields = `
            <div class="form-group">
                <label for="numero">Numéro *</label>
                <input type="text" id="numero" name="numero" required>
            </div>
            <div class="form-group">
                <label for="titre">Titre *</label>
                <input type="text" id="titre" name="titre" required>
            </div>
            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" rows="3"></textarea>
            </div>
            <div class="form-group">
                <label for="client_id">Client *</label>
                <select id="client_id" name="client_id" required></select>
            </div>
        `;
    } else if (type === 'echeance') {
        title.textContent = id ? 'Modifier l\'Échéance' : 'Nouvelle Échéance';
        fields = `
            <div class="form-group">
                <label for="titre">Titre *</label>
                <input type="text" id="titre" name="titre" required>
            </div>
            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" rows="3"></textarea>
            </div>
            <div class="form-group">
                <label for="date_echeance">Date d'échéance *</label>
                <input type="datetime-local" id="date_echeance" name="date_echeance" required>
            </div>
            <div class="form-group">
                <label for="affaire_id">Affaire *</label>
                <select id="affaire_id" name="affaire_id" required></select>
            </div>
        `;
    } else if (type === 'document') {
        title.textContent = id ? 'Modifier le Document' : 'Nouveau Document';
        if (!id) {
            fields = `
                <div class="form-group">
                    <label for="fichier">Fichier * (20 Mo maximum)</label>
                    <input type="file" id="fichier" name="fichier" required>
                </div>
            `;
        }
        fields += `
            <div class="form-group">
                <label for="nom">Nom${id ? ' *' : ' (par défaut : nom du fichier)'}</label>
                <input type="text" id="nom" name="nom" ${id ? 'required' : ''}>
            </div>
            <div class="form-group">
                <label for="affaire_id">Affaire *</label>
                <select id="affaire_id" name="affaire_id" required></select>
            </div>
        `;
    } else if (type === 'utilisateur') {
        title.textContent = 'Nouvel Utilisateur';
        fields = `
            <div class="form-group">
                <label for="username">Nom d'utilisateur *</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="email">Email *</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Mot de passe * (8 caractères minimum)</label>
                <input type="password" id="password" name="password" minlength="8" autocomplete="new-password" required>
            </div>
        `;
    }

    fields += `
        <div class="form-actions">
            <button type="button" class="btn" onclick="closeModal()">Annuler</button>
            <button type="submit" class="btn btn-primary">Enregistrer</button>
        </div>
    `;
    
    form.innerHTML = fields;
    form.onsubmit = (e) => handleSubmit(e, type, id);
    
    modal.classList.add('active');

    // Charger les listes déroulantes avant de pré-remplir le formulaire
    if (type === 'affaire') await loadClientsForSelect();
    if (type === 'echeance' || type === 'document') await loadAffairesForSelect();

    // Si modification, charger les données
    if (id) loadDataForEdit(type, id);
}

function closeModal() {
    document.getElementById('modal').classList.remove('active');
}

// API Calls
async function apiFetch(url, options = {}) {
    options.headers = { ...options.headers, 'Authorization': `Bearer ${getToken()}` };
    const response = await fetch(`${API_BASE}${url}`, options);
    if (response.status === 401) {
        redirectToLogin();
        throw new Error('Session expirée');
    }
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Erreur API');
    }
    return response;
}

async function apiCall(url, method = 'GET', data = null) {
    const options = { method, headers: {} };
    if (data instanceof FormData) {
        // Le navigateur définit lui-même le Content-Type multipart
        options.body = data;
    } else if (data) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(data);
    }

    const response = await apiFetch(url, options);
    return response.status === 204 ? null : response.json();
}

// Clients
async function loadClients() {
    try {
        const search = document.getElementById('search-clients')?.value || '';
        const url = search ? `/api/clients/?search=${encodeURIComponent(search)}` : '/api/clients/';
        const clients = await apiCall(url);
        const container = document.getElementById('clients-list');
        container.innerHTML = clients.map(c => `
            <div class="card">
                <h3>${c.prenom} ${c.nom}</h3>
                <p>📧 ${c.email}</p>
                <p>📞 ${c.telephone || 'Non renseigné'}</p>
                <p>📍 ${c.adresse || 'Non renseignée'}</p>
                <div class="actions">
                    <button class="edit" onclick="openModal('client', ${c.id})">Modifier</button>
                    <button class="delete" onclick="deleteClient(${c.id})">Supprimer</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

async function loadClientsForSelect() {
    try {
        const clients = await apiCall('/api/clients/');
        const select = document.getElementById('client_id');
        select.innerHTML = clients.map(c => 
            `<option value="${c.id}">${c.prenom} ${c.nom}</option>`
        ).join('');
    } catch (error) {
        console.error(error);
    }
}

async function deleteClient(id) {
    if (!confirm('Supprimer ce client ?')) return;
    try {
        await apiCall(`/api/clients/${id}`, 'DELETE');
        loadClients();
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Affaires
async function loadAffaires() {
    try {
        const search = document.getElementById('search-affaires')?.value || '';
        const statut = document.getElementById('filter-statut')?.value || '';
        
        let url = '/api/affaires/?';
        const params = [];
        if (search) params.push(`search=${encodeURIComponent(search)}`);
        if (statut) params.push(`statut=${encodeURIComponent(statut)}`);
        url += params.join('&');
        
        const affaires = await apiCall(url);
        const container = document.getElementById('affaires-list');
        container.innerHTML = affaires.map(a => `
            <div class="card">
                <h3>${a.titre}</h3>
                <p><strong>N°:</strong> ${a.numero}</p>
                <p><strong>Client:</strong> ${a.client_id}</p>
                <p><strong>Statut:</strong> <span class="badge badge-${a.statut}">${a.statut}</span></p>
                <p><strong>Ouverte le:</strong> ${new Date(a.date_ouverture).toLocaleDateString('fr-FR')}</p>
                <div class="actions">
                    <button class="edit" onclick="openModal('affaire', ${a.id})">Modifier</button>
                    <button class="delete" onclick="deleteAffaire(${a.id})">Supprimer</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

async function loadAffairesForSelect() {
    try {
        const affaires = await apiCall('/api/affaires/');
        const select = document.getElementById('affaire_id');
        select.innerHTML = affaires.map(a => 
            `<option value="${a.id}">${a.numero} - ${a.titre}</option>`
        ).join('');
    } catch (error) {
        console.error(error);
    }
}

async function deleteAffaire(id) {
    if (!confirm('Supprimer cette affaire ?')) return;
    try {
        await apiCall(`/api/affaires/${id}`, 'DELETE');
        loadAffaires();
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Échéances
async function loadEcheances() {
    try {
        const search = document.getElementById('search-echeances')?.value || '';
        const accomplie = document.getElementById('filter-accomplie')?.value || '';
        
        let url = '/api/echeances/?';
        const params = [];
        if (search) params.push(`search=${encodeURIComponent(search)}`);
        if (accomplie !== '') params.push(`accomplie=${encodeURIComponent(accomplie)}`);
        url += params.join('&');
        
        const echeances = await apiCall(url);
        const container = document.getElementById('echeances-list');
        container.innerHTML = echeances.map(e => `
            <div class="card">
                <h3>${e.titre}</h3>
                <p><strong>Date:</strong> ${new Date(e.date_echeance).toLocaleDateString('fr-FR')}</p>
                <p><strong>Affaire:</strong> ${e.affaire_id}</p>
                <p><strong>Statut:</strong> <span class="badge ${e.accomplie ? 'badge-accomplie' : 'badge-non-accomplie'}">${e.accomplie ? 'Accomplie' : 'En attente'}</span></p>
                <div class="actions">
                    <button class="edit" onclick="openModal('echeance', ${e.id})">Modifier</button>
                    <button class="delete" onclick="deleteEcheance(${e.id})">Supprimer</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

async function deleteEcheance(id) {
    if (!confirm('Supprimer cette échéance ?')) return;
    try {
        await apiCall(`/api/echeances/${id}`, 'DELETE');
        loadEcheances();
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Documents
function formatTaille(octets) {
    if (octets < 1024) return `${octets} o`;
    if (octets < 1024 * 1024) return `${(octets / 1024).toFixed(1)} Ko`;
    return `${(octets / (1024 * 1024)).toFixed(1)} Mo`;
}

async function loadDocuments() {
    try {
        const search = document.getElementById('search-documents')?.value || '';
        const affaireId = document.getElementById('filter-document-affaire')?.value || '';

        let url = '/api/documents/?';
        const params = [];
        if (search) params.push(`search=${encodeURIComponent(search)}`);
        if (affaireId) params.push(`affaire_id=${encodeURIComponent(affaireId)}`);
        url += params.join('&');

        const documents = await apiCall(url);
        const container = document.getElementById('documents-list');
        if (documents.length === 0) {
            container.innerHTML = '<p class="empty">Aucun document</p>';
            return;
        }
        container.innerHTML = documents.map(d => `
            <div class="card">
                <h3>📄 ${escapeHtml(d.nom)}</h3>
                <p><strong>Type:</strong> ${escapeHtml(d.type_mime || 'Inconnu')}</p>
                <p><strong>Taille:</strong> ${formatTaille(d.taille)}</p>
                <p><strong>Affaire:</strong> ${d.affaire_id}</p>
                <p><strong>Ajouté le:</strong> ${new Date(d.date_creation).toLocaleDateString('fr-FR')}</p>
                <div class="actions">
                    <button class="download" onclick="downloadDocument(${d.id})">Télécharger</button>
                    <button class="edit" onclick="openModal('document', ${d.id})">Modifier</button>
                    <button class="delete" onclick="deleteDocument(${d.id})">Supprimer</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

async function loadAffairesForFilter() {
    try {
        const affaires = await apiCall('/api/affaires/');
        const select = document.getElementById('filter-document-affaire');
        const current = select.value;
        select.innerHTML = '<option value="">Toutes les affaires</option>' + affaires.map(a =>
            `<option value="${a.id}">${escapeHtml(a.numero)} - ${escapeHtml(a.titre)}</option>`
        ).join('');
        select.value = current;
    } catch (error) {
        console.error(error);
    }
}

async function downloadDocument(id) {
    try {
        const doc = await apiCall(`/api/documents/${id}`);
        const response = await apiFetch(`/api/documents/${id}/telecharger`);
        const url = URL.createObjectURL(await response.blob());
        const link = document.createElement('a');
        link.href = url;
        link.download = doc.nom;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

async function deleteDocument(id) {
    if (!confirm('Supprimer ce document ?')) return;
    try {
        await apiCall(`/api/documents/${id}`, 'DELETE');
        loadDocuments();
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Notifications
async function loadNotifications() {
    try {
        const notifications = await apiCall('/api/notifications/');
        const nonLues = notifications.filter(n => !n.lue).length;
        const count = document.getElementById('notif-count');
        count.textContent = nonLues;
        count.classList.toggle('hidden', nonLues === 0);

        const list = document.getElementById('notif-list');
        if (notifications.length === 0) {
            list.innerHTML = '<p class="empty">Aucune notification</p>';
            return;
        }
        list.innerHTML = notifications.map(n => `
            <div class="notif-item ${n.lue ? '' : 'unread'}" onclick="markNotificationRead(${n.id})">
                <h4>${escapeHtml(n.titre)}</h4>
                <p>${escapeHtml(n.message)}</p>
                <small>${new Date(n.date_creation).toLocaleString('fr-FR')}</small>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erreur chargement notifications:', error);
    }
}

function toggleNotifications() {
    document.getElementById('notif-panel').classList.toggle('active');
}

async function markNotificationRead(id) {
    try {
        await apiCall(`/api/notifications/${id}/lue`, 'PUT');
        loadNotifications();
    } catch (error) {
        console.error(error);
    }
}

async function markAllNotificationsRead() {
    try {
        await apiCall('/api/notifications/lire-tout', 'PUT');
        loadNotifications();
    } catch (error) {
        console.error(error);
    }
}

// Form handling
async function handleSubmit(e, type, id) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    try {
        if (type === 'utilisateur') {
            await apiCall('/api/auth/register', 'POST', data);
            closeModal();
            alert(`Utilisateur « ${data.username} » créé`);
            return;
        }
        if (type === 'document' && !id) {
            // Upload multipart (fichier + métadonnées)
            await apiCall('/api/documents/', 'POST', formData);
            closeModal();
            loadDocuments();
            return;
        }
    } catch (error) {
        alert('Erreur: ' + error.message);
        return;
    }

    // Convertir les types
    if (type === 'client') {
        // Les chaînes sont OK
    } else if (type === 'affaire') {
        data.client_id = parseInt(data.client_id);
    } else if (type === 'echeance') {
        data.affaire_id = parseInt(data.affaire_id);
        data.date_echeance = new Date(data.date_echeance).toISOString();
    } else if (type === 'document') {
        data.affaire_id = parseInt(data.affaire_id);
    }
    
    try {
        if (id) {
            await apiCall(`/api/${type}s/${id}`, 'PUT', data);
        } else {
            await apiCall(`/api/${type}s/`, 'POST', data);
        }
        closeModal();
        // Recharger la liste
        if (type === 'client') loadClients();
        else if (type === 'affaire') loadAffaires();
        else if (type === 'echeance') loadEcheances();
        else if (type === 'document') loadDocuments();
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

async function loadDataForEdit(type, id) {
    try {
        const data = await apiCall(`/api/${type}s/${id}`);
        // Remplir le formulaire
        Object.keys(data).forEach(key => {
            const input = document.getElementById(key);
            if (input) {
                if (key.includes('date')) {
                    input.value = new Date(data[key]).toISOString().slice(0, 16);
                } else {
                    input.value = data[key];
                }
            }
        });
    } catch (error) {
        console.error(error);
    }
}

// Documents
async function loadDocuments() {
    try {
        const affaireId = document.getElementById('filter-docs-affaire')?.value || '';
        const url = affaireId ? `/api/documents/?affaire_id=${affaireId}` : '/api/documents/';
        const documents = await apiCall(url);
        const container = document.getElementById('documents-list');
        container.innerHTML = documents.map(d => `
            <div class="card">
                <h3>${d.nom}</h3>
                <p><strong>Type:</strong> ${d.type_mime || 'Inconnu'}</p>
                <p><strong>Taille:</strong> ${formatFileSize(d.taille)}</p>
                <p><strong>Affaire:</strong> ${d.affaire_id}</p>
                <p><strong>Ajouté le:</strong> ${new Date(d.date_creation).toLocaleDateString('fr-FR')}</p>
                <div class="actions">
                    <button class="edit" onclick="downloadDocument(${d.id})">Télécharger</button>
                    <button class="delete" onclick="deleteDocument(${d.id})">Supprimer</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

async function loadAffairesForDocs() {
    try {
        const affaires = await apiCall('/api/affaires/');
        const select = document.getElementById('filter-docs-affaire');
        select.innerHTML = '<option value="">Toutes les affaires</option>' + 
            affaires.map(a => `<option value="${a.id}">${a.numero} - ${a.titre}</option>`).join('');
    } catch (error) {
        console.error(error);
    }
}

async function downloadDocument(id) {
    window.open(`/api/documents/download/${id}`, '_blank');
}

async function deleteDocument(id) {
    if (!confirm('Supprimer ce document ?')) return;
    try {
        await apiCall(`/api/documents/${id}`, 'DELETE');
        loadDocuments();
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

function formatFileSize(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});
