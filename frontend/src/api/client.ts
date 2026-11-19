const API_BASE = import.meta.env.VITE_API_URL ?? ''

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || response.statusText)
  }
  return response.json() as Promise<T>
}

export type CreateCampaignBody = {
  name: string
  geo: string
  offer_id: number
}

export type CreateCampaignResponse = {
  id: number
  name: string
  keitaro_campaign_id: number
  offer_stream_id: number
  geo_countries: string
}

export type OfferSearchItem = { id: number; name: string }

export type OfferStats = {
  id: number
  share: number
  clicks: number
  unique: number
  bots: number
}

export type CampaignState = {
  id: number
  name: string
  geo_countries: string
  keitaro_campaign_id: number
  offer_stream_id: number
  offers: OfferStats[]
}

export const api = {
  createCampaign: (body: CreateCampaignBody) =>
    request<CreateCampaignResponse>('/api/campaigns', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  searchOffers: (q: string) =>
    request<OfferSearchItem[]>(`/api/offers?q=${encodeURIComponent(q)}`),
  getCampaign: (id: number) => request<CampaignState>(`/api/campaigns/${id}`),
  addOffer: (campaignId: number, offerId: number) =>
    request<CampaignState>(`/api/campaigns/${campaignId}/offers`, {
      method: 'POST',
      body: JSON.stringify({ offer_id: offerId }),
    }),
  removeOffer: (campaignId: number, offerId: number) =>
    request<CampaignState>(`/api/campaigns/${campaignId}/offers/${offerId}`, {
      method: 'DELETE',
    }),
}