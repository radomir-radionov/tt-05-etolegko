from app.models.campaign_record import CampaignRecord


def test_campaign_record_persists(db_session):
    record = CampaignRecord(
        name="test_radionov_x",
        geo_countries="MX,AU",
        keitaro_campaign_id=1,
        offer_stream_id=2,
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)

    assert record.id is not None
    saved = db_session.get(CampaignRecord, record.id)
    assert saved is not None
    assert saved.name == "test_radionov_x"