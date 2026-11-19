import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, afterEach, describe, expect, it } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { CreateCampaignPage } from './CreateCampaignPage'

describe('CreateCampaignPage', () => {
  const originalFetch = global.fetch

  beforeEach(() => {
    global.fetch = async (input, init) => {
      const url = String(input)
      if (url.includes('/api/offers')) {
        return new Response(JSON.stringify([{ id: 18813, name: 'Sample Offer' }]), {
          status: 200,
        })
      }
      if (url.includes('/api/campaigns') && init?.method === 'POST') {
        const body = JSON.parse(String(init.body))
        expect(body).toMatchObject({
          name: 'test_radionov_demo',
          geo: 'MX,AU',
          offer_id: 18813,
        })
        return new Response(
          JSON.stringify({
            id: 1,
            name: body.name,
            keitaro_campaign_id: 12345,
            offer_stream_id: 99,
            geo_countries: 'MX,AU',
          }),
          { status: 201 },
        )
      }
      return new Response('not found', { status: 404 })
    }
  })

  afterEach(() => {
    global.fetch = originalFetch
  })

  it('submits campaign creation', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <CreateCampaignPage />
      </MemoryRouter>,
    )

    await user.clear(screen.getByPlaceholderText('test_radionov_campaign1'))
    await user.type(
      screen.getByPlaceholderText('test_radionov_campaign1'),
      'test_radionov_demo',
    )
    await user.clear(screen.getByPlaceholderText('MX,AU,RO,...'))
    await user.type(screen.getByPlaceholderText('MX,AU,RO,...'), 'MX,AU')
    await user.type(screen.getByPlaceholderText('search offers'), 'sam')
    await waitFor(() =>
      expect(screen.getByText(/\[18813\]/)).toBeInTheDocument(),
    )
    await user.click(screen.getByText(/\[18813\]/))
    await user.click(screen.getByRole('button', { name: 'Create' }))

    await waitFor(() =>
      expect(screen.getByText(/Keitaro campaign 12345/)).toBeInTheDocument(),
    )
  })
})