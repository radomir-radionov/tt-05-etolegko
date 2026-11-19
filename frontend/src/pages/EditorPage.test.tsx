import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { EditorPage } from './EditorPage'

describe('EditorPage', () => {
  const originalFetch = global.fetch
  let offers = [
    { id: 10, share: 50, clicks: 7, unique: 4, bots: 1 },
    { id: 20, share: 50, clicks: 2, unique: 2, bots: 0 },
  ]

  beforeEach(() => {
    offers = [
      { id: 10, share: 50, clicks: 7, unique: 4, bots: 1 },
      { id: 20, share: 50, clicks: 2, unique: 2, bots: 0 },
    ]
    global.fetch = async (input, init) => {
      const url = String(input)
      const method = init?.method ?? 'GET'
      if (url.includes('/api/campaigns/1') && method === 'GET') {
        return new Response(
          JSON.stringify({
            id: 1,
            name: 'test_radionov_ed',
            geo_countries: 'AU',
            keitaro_campaign_id: 77,
            offer_stream_id: 55,
            offers,
          }),
          { status: 200 },
        )
      }
      if (url.includes('/offers/20') && method === 'DELETE') {
        offers = offers.filter((o) => o.id !== 20)
        return new Response(
          JSON.stringify({
            id: 1,
            name: 'test_radionov_ed',
            geo_countries: 'AU',
            keitaro_campaign_id: 77,
            offer_stream_id: 55,
            offers,
          }),
          { status: 200 },
        )
      }
      return new Response('not found', { status: 404 })
    }
  })

  afterEach(() => {
    global.fetch = originalFetch
  })

  it('removes an offer and updates stats row', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter initialEntries={['/campaigns/1/editor']}>
        <Routes>
          <Route path="/campaigns/:id/editor" element={<EditorPage />} />
        </Routes>
      </MemoryRouter>,
    )

    await waitFor(() => expect(screen.getByText('10')).toBeInTheDocument())
    expect(screen.getByText('20')).toBeInTheDocument()
    const removeButtons = screen.getAllByRole('button', { name: 'Remove' })
    await user.click(removeButtons[1])
    await waitFor(() => expect(screen.queryByText('20')).not.toBeInTheDocument())
    expect(screen.getByText('7')).toBeInTheDocument()
  })
})