import random
from datetime import date, datetime

from fastapi_rtk import db, g
from fastapi_rtk.utils import safe_call
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .models import Application, Asset, Unit


async def add_base_data():
    await g.current_app.security.create_user(
        username="admin",
        email="admin@test.com",
        password="admin",
        first_name="Admin",
        last_name="Admin",
        roles=[g.admin_role],
        raise_exception=False,
    )

    async with db.session("assets") as session:
        for i in range(100):
            asset = Asset(
                name=f"asset&{i}", date_time=datetime.now(), date=date.today()
            )
            if i % 10 == 0:
                unit = Unit(name=f"unit&{int(i / 10)}")
                session.add(unit)
            asset.owner = unit
            session.add(asset)

        for i in range(20):
            application = Application(name=f"application_{i}", description=f"info_{i}")
            session.add(application)

        stmt = select(Asset).options(selectinload(Asset.applications))
        result = await safe_call(session.execute(stmt))
        assets = result.scalars().all()
        stmt = select(Application)
        result = await safe_call(session.execute(stmt))
        applications = result.scalars().all()

        for i, asset in enumerate(assets):
            for j in range(
                1, len(assets) // len(applications) + 1
            ):  # Associate each asset with 5 applications
                application = applications[random.randint(1, len(applications) - 1)]
                asset.applications.append(application)

        await safe_call(session.commit())
