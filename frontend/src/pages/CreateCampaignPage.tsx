import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { api, type OfferSearchItem } from '../api/client'

export function CreateCampaignPage() {
  const [name, setName] = useState('test_radionov_')
  const [geo, setGeo] = useState('MX,AU,RO')
  const [offerQuery, setOfferQuery] = useState('')
  const [offers, setOffers] = useState<OfferSearchItem[]>([])
  const [offerId, setOfferId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<{ id: number; keitaroId: number } | null>(
    null,
  )
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (offerQuery.trim().length < 2) {
      setOffers([])
      return
    }
    const timer = setTimeout(() => {
      api
        .searchOffers(offerQuery)
        .then(setOffers)
        .catch(() => setOffers([]))
    }, 300)
    return () => clearTimeout(timer)
  }, [offerQuery])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (offerId === null) {
      setError('Select an offer')
      return
    }
    setSubmitting(true)
    setError(null)
    setSuccess(null)
    try {
      const result = await api.createCampaign({
        name,
        geo,
        offer_id: offerId,
      })
      setSuccess({ id: result.id, keitaroId: result.keitaro_campaign_id })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="page">
      <h1>New campaign</h1>
      <form className="card" onSubmit={onSubmit}>
        <label>
          Name
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="test_radionov_campaign1"
          />
        </label>
        <label>
          Geo
          <input
            value={geo}
            onChange={(e) => setGeo(e.target.value)}
            placeholder="MX,AU,RO,..."
          />
        </label>
        <label>
          Offer
          <input
            value={offerQuery}
            onChange={(e) => setOfferQuery(e.target.value)}
            placeholder="search offers"
          />
        </label>
        {offers.length > 0 && (
          <ul className="offer-list">
            {offers.map((offer) => (
              <li key={offer.id}>
                <button
                  type="button"
                  className={offerId === offer.id ? 'selected' : ''}
                  onClick={() => setOfferId(offer.id)}
                >
                  [{offer.id}] {offer.name}
                </button>
              </li>
            ))}
          </ul>
        )}
        <button type="submit" disabled={submitting}>
          Create
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {success && (
        <p className="success">
          Created local id {success.id}, Keitaro campaign {success.keitaroId}.{' '}
          <Link to={`/campaigns/${success.id}/editor`}>Open editor</Link>
        </p>
      )}
    </main>
  )
}