import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { api, type CampaignState, type OfferSearchItem } from '../api/client'

export function EditorPage() {
  const { id } = useParams()
  const campaignId = Number(id)
  const [state, setState] = useState<CampaignState | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [offerQuery, setOfferQuery] = useState('')
  const [offers, setOffers] = useState<OfferSearchItem[]>([])
  const [addOfferId, setAddOfferId] = useState('')

  const load = useCallback(() => {
    if (!Number.isFinite(campaignId)) {
      return
    }
    api
      .getCampaign(campaignId)
      .then(setState)
      .catch((err) =>
        setError(err instanceof Error ? err.message : 'Failed to load'),
      )
  }, [campaignId])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    if (offerQuery.trim().length < 2) {
      setOffers([])
      return
    }
    const timer = setTimeout(() => {
      api.searchOffers(offerQuery).then(setOffers).catch(() => setOffers([]))
    }, 300)
    return () => clearTimeout(timer)
  }, [offerQuery])

  async function onAdd(e: FormEvent) {
    e.preventDefault()
    const offerId = Number(addOfferId)
    if (!offerId) {
      return
    }
    try {
      const next = await api.addOffer(campaignId, offerId)
      setState(next)
      setAddOfferId('')
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Add failed')
    }
  }

  async function onRemove(offerId: number) {
    try {
      const next = await api.removeOffer(campaignId, offerId)
      setState(next)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Remove failed')
    }
  }

  if (!state) {
    return (
      <main className="page">
        <p>{error ?? 'Loading…'}</p>
      </main>
    )
  }

  return (
    <main className="page">
      <h1>Campaign editor</h1>
      <p>
        <strong>{state.name}</strong> (Keitaro #{state.keitaro_campaign_id})
      </p>
      <table>
        <thead>
          <tr>
            <th>Offer ID</th>
            <th>Share %</th>
            <th>Clicks</th>
            <th>Unique</th>
            <th>Bots</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {state.offers.map((offer) => (
            <tr key={offer.id}>
              <td>{offer.id}</td>
              <td>{offer.share}</td>
              <td>{offer.clicks}</td>
              <td>{offer.unique}</td>
              <td>{offer.bots}</td>
              <td>
                <button type="button" onClick={() => onRemove(offer.id)}>
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <form className="card row" onSubmit={onAdd}>
        <input
          value={offerQuery}
          onChange={(e) => setOfferQuery(e.target.value)}
          placeholder="search offer"
        />
        <input
          value={addOfferId}
          onChange={(e) => setAddOfferId(e.target.value)}
          placeholder="offer id"
        />
        <button type="submit">Add</button>
      </form>
      {offers.length > 0 && (
        <ul className="offer-list">
          {offers.map((offer) => (
            <li key={offer.id}>
              <button type="button" onClick={() => setAddOfferId(String(offer.id))}>
                [{offer.id}] {offer.name}
              </button>
            </li>
          ))}
        </ul>
      )}
      {error && <p className="error">{error}</p>}
    </main>
  )
}