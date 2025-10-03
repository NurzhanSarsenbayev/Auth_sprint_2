import pytest
from django.urls import reverse
from movies.models import Person


@pytest.mark.django_db
def test_admin_person_crud(logged_client):
    """CRUD для персон через админку"""

    # ➕ Добавляем персону
    add_url = reverse("admin:movies_person_add")
    resp = logged_client.post(
        add_url,
        {"full_name": "John Smith"},
        follow=True
    )
    assert resp.status_code == 200
    assert Person.objects.filter(full_name="John Smith").exists()

    # ✏️ Редактируем персону
    person = Person.objects.get(full_name="John Smith")
    change_url = reverse("admin:movies_person_change", args=[person.id])
    resp = logged_client.post(
        change_url,
        {"full_name": "John Updated"},
        follow=True
    )
    assert resp.status_code == 200
    person.refresh_from_db()
    assert person.full_name == "John Updated"

    # ❌ Удаляем персону
    delete_url = reverse("admin:movies_person_delete", args=[person.id])
    resp = logged_client.post(delete_url, {"post": "yes"}, follow=True)
    assert resp.status_code == 200
    assert not Person.objects.filter(id=person.id).exists()
