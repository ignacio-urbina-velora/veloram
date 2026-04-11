/**
 * API client for communicating with the FastAPI backend.
 */

export const API_BASE = process.env.NODE_ENV === 'production' ? 'https://ai-video-backend-api-production.up.railway.app' : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

interface TokenPair {
    access_token: string;
    refresh_token: string;
}

class ApiClient {
    private accessToken: string | null = null;

    constructor() {
        if (typeof window !== 'undefined') {
            this.accessToken = localStorage.getItem('access_token');
        }
    }

    setTokens(tokens: TokenPair) {
        this.accessToken = tokens.access_token;
        if (typeof window !== 'undefined') {
            localStorage.setItem('access_token', tokens.access_token);
            localStorage.setItem('refresh_token', tokens.refresh_token);
        }
    }

    clearTokens() {
        this.accessToken = null;
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        }
    }

    private async fetch(path: string, options: RequestInit = {}) {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...(options.headers as Record<string, string> || {}),
        };

        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        // Ensure path starts with /api if not already present
        const apiPath = (path && path.startsWith('/api')) ? path : `/api${path || ''}`;

        const res = await fetch(`${API_BASE}${apiPath}`, {
            ...options,
            headers,
        });

        if (res.status === 401) {
            this.clearTokens();
            if (typeof window !== 'undefined') {
                window.location.href = '/login';
            }
            throw new Error('Unauthorized');
        }

        if (!res.ok) {
            const error = await res.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(error.detail || `HTTP ${res.status}`);
        }

        if (res.status === 204) return null;
        return res.json();
    }

    // Auth
    async register(email: string, username: string, password: string) {
        const data = await this.fetch('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, username, password }),
        });
        this.setTokens(data);
        return data;
    }

    async login(email: string, password: string) {
        const data = await this.fetch('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        this.setTokens(data);
        return data;
    }

    async loginWithToken(email: string, token: string) {
        const data = await this.fetch('/auth/login-token', {
            method: 'POST',
            body: JSON.stringify({ email, token }),
        });
        this.setTokens(data);
        return data;
    }

    async getMe() {
        return this.fetch('/auth/me');
    }

    getUser() {
        if (!this.accessToken) return null;
        try {
            const payload = JSON.parse(atob(this.accessToken.split('.')[1]));
            return {
                id: parseInt(payload.sub),
                username: payload.username || 'User',
                email: payload.email
            };
        } catch (e) {
            return null;
        }
    }

    async forgotPassword(email: string) {
        return this.fetch('/auth/forgot-password', {
            method: 'POST',
            body: JSON.stringify({ email }),
        });
    }

    // Tiers
    async getTiers() {
        return this.fetch('/tiers');
    }

    // Projects
    async createProject(data: {
        title: string;
        tier: number;
        avatar_id?: number;
        target_duration_sec?: number;
        global_prompt?: string;
        style_preset?: string;
        is_mock?: boolean;
        shots: Array<{
            prompt: string;
            camera_movement?: string;
            lighting?: string;
            mood?: string;
            dialogue?: string;
            negative_prompt?: string;
            duration_target_sec?: number;
        }>;
    }) {
        return this.fetch('/projects/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getProjects() {
        return this.fetch('/projects/');
    }

    async getProject(id: number) {
        return this.fetch(`/projects/${id}`);
    }

    async updateShot(projectId: number, shotId: number, data: Record<string, unknown>) {
        return this.fetch(`/projects/${projectId}/shots/${shotId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async directorRefineSequence(shots: any[], feedback: string) {
        return this.fetch('/director/refine-sequence', {
            method: 'POST',
            body: JSON.stringify({ shots, feedback })
        });
    }

    async addShot(projectId: number, data: Record<string, unknown>) {
        return this.fetch(`/projects/${projectId}/shots`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async deleteShot(projectId: number, shotId: number) {
        return this.fetch(`/projects/${projectId}/shots/${shotId}`, {
            method: 'DELETE',
        });
    }

    async startGeneration(projectId: number) {
        return this.fetch(`/projects/${projectId}/generate`, {
            method: 'POST',
        });
    }

    async getEstimate(tier: number, shotsCount: number = 5) {
        return this.fetch(`/projects/estimate/${tier}?shots_count=${shotsCount}`);
    }

    async refinePrompt(prompt: string, context?: string) {
        return this.fetch('/projects/refine-prompt', {
            method: 'POST',
            body: JSON.stringify({ prompt, context }),
        });
    }

    async startShotGeneration(projectId: number, shotId: number) {
        return this.fetch(`/projects/${projectId}/shots/${shotId}/generate`, {
            method: 'POST',
        });
    }

    // Jobs / Progress
    async getProjectJobs(projectId: number) {
        return this.fetch(`/jobs/project/${projectId}`);
    }

    subscribeProgress(projectId: number, onMessage: (data: unknown) => void) {
        const evtSource = new EventSource(
            `${API_BASE}/jobs/project/${projectId}/progress`
        );
        evtSource.onmessage = (e) => onMessage(JSON.parse(e.data));
        evtSource.onerror = () => evtSource.close();
        return evtSource;
    }

    // Admin
    async getAdminStats() {
        return this.fetch('/admin/stats');
    }

    async getAdminUsers() {
        return this.fetch('/admin/users');
    }

    async getAdminQueue() {
        return this.fetch('/admin/queue');
    }

    async getAdminReferrals() {
        return this.fetch('/admin/referrals');
    }

    async getAdminAffiliates() {
        return this.fetch('/admin/affiliates');
    }

    async processPayout(affiliateId: number, amount: number) {
        return this.fetch(`/admin/affiliates/${affiliateId}/payout`, {
            method: 'POST',
            body: JSON.stringify({ amount }),
        });
    }

    // Reasoning
    async getAiReasoning(prompt: string, projectId?: number, systemPrompt?: string) {
        return this.fetch('/reasoning', {
            method: 'POST',
            body: JSON.stringify({ prompt, project_id: projectId, system_prompt: systemPrompt }),
        });
    }

    async planVideo(idea: string, durationMinutes: number = 15, style: string = 'cinematic') {
        return this.fetch('/reasoning/plan', {
            method: 'POST',
            body: JSON.stringify({ idea, duration_minutes: durationMinutes, style }),
        });
    }

    async refineShot(shotPrompt: string, context: string = '') {
        return this.fetch('/reasoning/refine', {
            method: 'POST',
            body: JSON.stringify({ shot_prompt: shotPrompt, context }),
        });
    }

    async checkCoherence(shots: Array<Record<string, unknown>>) {
        return this.fetch('/reasoning/coherence', {
            method: 'POST',
            body: JSON.stringify({ shots }),
        });
    }

    // Director Brain
    async directorPlan(idea: string, targetDurationSec: number = 15, style: string = 'cinematic') {
        return this.fetch('/api/director/plan', {
            method: 'POST',
            body: JSON.stringify({ idea, target_duration_sec: targetDurationSec, style }),
        });
    }

    async directorRefine(shot: any, feedback: string) {
        return this.fetch('/api/director/refine', {
            method: 'POST',
            body: JSON.stringify({ shot, feedback }),
        });
    }

    async directorHealth() {
        return this.fetch('/api/director/health');
    }

    // Affiliates
    async getAffiliateMe() {
        return this.fetch('/affiliates/me');
    }

    async applyAffiliate(data: { code: string; payment_method?: string; payment_details?: string }) {
        return this.fetch('/affiliates/apply', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async checkAffiliateCode(code: string) {
        return this.fetch('/affiliates/check-code', {
            method: 'POST',
            body: JSON.stringify({ code }),
        });
    }

    // Avatars
    async generateAvatar(params: {
        gender?: string;
        age?: number;
        height?: number;
        weight?: number;
        build?: string;
        country?: string;
        eyes?: string;
        hairstyle?: string;
        hair_color?: string;
        breast_size?: string | null;
        clothing?: string;
        extra_prompt?: string;
        negative_prompt?: string;
        base_image_b64?: string;
    }): Promise<{ image_b64: string; prompt_used: string; credits_deducted: number }> {
        return this.fetch('/avatars/generate', {
            method: 'POST',
            body: JSON.stringify(params),
        });
    }

    async saveAvatar(params: {
        name: string;
        image_b64: string;
        refined_image_b64?: string;   // Imagen HD (Flux ControlNet) — se convierte en imagen principal
        morphs?: Record<string, number>;
        styles?: Record<string, string>;
    }): Promise<{ id: number; name: string; texture_url: string; message: string }> {
        return this.fetch('/avatars/save', {
            method: 'POST',
            body: JSON.stringify(params),
        });
    }

    async listAvatars(): Promise<Array<{
        id: number;
        name: string;
        texture_url: string;
        status: string;
        created_at: string;
        styles?: Record<string, string>;
        morphs?: Record<string, number>;
    }>> {
        return this.fetch('/avatars/');
    }

    async deleteAvatar(id: number): Promise<void> {
        return this.fetch(`/avatars/${id}`, { method: 'DELETE' });
    }

    async generatePortrait(params: {
        gender?: string;
        age?: number;
        eyes?: string;
        hair_color?: string;
        hairstyle?: string;
        country?: string;
        prompt?: string;
        negative_prompt?: string;
        face_shape?: string;
        skin_tone?: string;
        eye_shape?: string;
        eyebrow_style?: string;
        hair_length?: string;
        bangs?: string;
        lip_volume?: string;
        lip_color?: string;
        makeup?: string;
        expression?: string;
        lighting?: string;
        tier?: string;
    }) {
        return this.fetch('/avatars/generate-portrait', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    async generateConsistentVariation(params: {
        avatar_id: number;
        prompt: string;
        face_weight?: number;
        seed?: number;
    }): Promise<{ image_b64: string; credits_remaining: number; avatar_id: number }> {
        return this.fetch('/avatars/generate-consistent', {
            method: 'POST',
            body: JSON.stringify(params),
        });
    }

    async projectFace(params: {
        face_image_b64: string;
        mannequin_glb_b64?: string;
    }): Promise<{ glb_base64: string; logs?: string }> {
        return this.fetch('/avatars/project-face', {
            method: 'POST',
            body: JSON.stringify(params),
        });
    }

    isLoggedIn(): boolean {
        return !!this.accessToken;
    }

    getToken(): string | null {
        return this.accessToken;
    }

    baseUrl(): string {
        return API_BASE;
    }
}

export const api = new ApiClient();
