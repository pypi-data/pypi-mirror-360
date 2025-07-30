import json
from types import SimpleNamespace

import httpx
import pytest

from fbnconfig import identity

TEST_BASE = "https://foo.lusid.com"


def response_hook(response: httpx.Response):
    response.raise_for_status()


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeIdentityRoleRef:
    # This should use the same method of creating a client as the host
    # To be refactored
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    def test_attach_when_exists(self, respx_mock):
        # given 2 roles in the system where role2 matches the sut
        respx_mock.get("/identity/api/roles").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": "11111111",
                        "roleId": {"scope": "default", "code": "role1"},
                        "name": "role1",
                        "description": "role one",
                    },
                    {
                        "id": "22222222",
                        "roleId": {"scope": "default", "code": "role2"},
                        "name": "role2",
                        "description": "role two",
                    },
                ],
            )
        )
        client = self.client
        # when we attach
        sut = identity.IdentityRoleRef(id="xyz", name="role2")
        sut.attach(client)
        # then the roleId property is populated from the response
        assert sut.role_id == "22222222"

    def test_attach_when_not_exists(self, respx_mock):
        # given 2 roles in the system where neither matches the sut
        respx_mock.get("/identity/api/roles").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": "11111111",
                        "roleId": {"scope": "default", "code": "role1"},
                        "name": "role1",
                        "description": "role one",
                    },
                    {
                        "id": "22222222",
                        "roleId": {"scope": "default", "code": "role2"},
                        "name": "role2",
                        "description": "role two",
                    },
                ],
            )
        )
        client = self.client
        # when we attach an exception is thrown
        sut = identity.IdentityRoleRef(id="xyz", name="none_of_those")
        with pytest.raises(RuntimeError):
            sut.attach(client)

    def test_attach_when_http_error(self, respx_mock):
        # given a server which returns a 500
        respx_mock.get("/identity/api/roles").mock(return_value=httpx.Response(500, json={}))
        client = self.client
        # when we attach a http exception is thrown
        sut = identity.IdentityRoleRef(id="xyz", name="none_of_those")
        with pytest.raises(httpx.HTTPStatusError):
            sut.attach(client)


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeIdentityRoleResource:
    client = httpx.Client(base_url=TEST_BASE)

    def test_create(self, respx_mock):
        respx_mock.post("/identity/api/roles").mock(
            return_value=httpx.Response(
                200, json={"id": "aaaaaa", "roleId": {"scope": "default", "code": "role1"}}
            )
        )
        # given a desired role
        sut = identity.IdentityRoleResource(id="role_id", name="role1", description="role one")
        # when we create it
        state = sut.create(self.client)
        # then the state is returned
        assert state == {
            "id": "role_id",
            "scope": "default",
            "name": "role1",
            "code": "role1",
            "roleId": "aaaaaa",
        }
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/identity/api/roles"
        assert json.loads(request.content) == {"name": "role1", "description": "role one"}

    def test_update_with_no_changes(self, respx_mock):
        respx_mock.get("/identity/api/roles/bxbxbx").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "bxbxbx",
                    "roleId": {"scope": "default", "code": "role_b"},
                    "source": "source1",
                    "samlName": "abcxxxx",
                    "name": "role_b",
                    "description": "role bee",
                },
            )
        )
        # given a desired role
        sut = identity.IdentityRoleResource(id="res_id", name="role_b", description="role bee")
        old_state = SimpleNamespace(
            roleId="bxbxbx", id="res_id", scope="default", code="role_b", name="role_b"
        )
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state is None
        assert state is None
        # and a read was made
        request = respx_mock.calls.last.request
        assert request.method == "GET"
        assert request.url.path == "/identity/api/roles/bxbxbx"
        # but no PUT

    def test_update_with_change_description(self, respx_mock):
        respx_mock.get("/identity/api/roles/bxbxbx").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "bxbxbx",
                    "roleId": {"scope": "default", "code": "role_b"},
                    "source": "source1",
                    "samlName": "abcxxxx",
                    "name": "role_b",
                    "description": "role bee",
                },
            )
        )
        respx_mock.put("/identity/api/roles/bxbxbx").mock(return_value=httpx.Response(200, json={}))
        # given a desired role
        sut = identity.IdentityRoleResource(
            id="res_id", name="role_b", description="modified description"
        )
        old_state = SimpleNamespace(
            roleId="bxbxbx", id="res_id", scope="default", code="role_b", name="role_b"
        )
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state is None
        assert state is None
        # and the put is sent
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/identity/api/roles/bxbxbx"
        assert json.loads(request.content) == {"description": "modified description"}

    def test_update_with_change_name_should_throw(self, respx_mock):
        # given a desired role
        sut = identity.IdentityRoleResource(id="res_id", name="modified_name", description="role bee")
        old_state = SimpleNamespace(
            roleId="bxbxbx", id="res_id", scope="default", code="role_b", name="role_b"
        )
        # when we update it throws
        with pytest.raises(RuntimeError):
            sut.update(self.client, old_state)

    def test_delete(self, respx_mock):
        respx_mock.delete("/identity/api/roles/bxbxbx").mock(return_value=httpx.Response(200, json={}))
        # given a role that exists
        old_state = SimpleNamespace(
            roleId="bxbxbx", id="res_id", scope="default", code="role_b", name="role_b"
        )
        # when we delete it
        identity.IdentityRoleResource.delete(self.client, old_state)
        # then a delete request is sent with the roleId
        request = respx_mock.calls.last.request
        assert request.method == "DELETE"
        assert request.url.path == "/identity/api/roles/bxbxbx"

    def test_deps(self):
        # given a desired role
        sut = identity.IdentityRoleResource(id="res_id", name="modified_name", description="role bee")
        # it's deps are empty
        assert sut.deps() == []


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeUserRef:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    def test_attach_exists(self, respx_mock):
        # given the user "match" exists in the remote
        respx_mock.get("/identity/api/users").mock(
            return_value=httpx.Response(
                200, json=[{"id": "cvex", "login": "no_match"}, {"id": "bdxe", "login": "match"}]
            )
        )
        # when we attach a UserRef
        sut = identity.UserRef(id="user", login="match")
        sut.attach(self.client)
        # then it's userId will be from the matching entry
        assert sut.user_id == "bdxe"

    def test_attach_when_not_exists(self, respx_mock):
        # given the user "match" does not exist
        respx_mock.get("/identity/api/users").mock(
            return_value=httpx.Response(
                200,
                json=[{"id": "cvex", "login": "no_match"}, {"id": "bdxe", "login": "other_no_match"}],
            )
        )
        # when we attach a UserRef
        sut = identity.UserRef(id="user", login="match")
        # an exception is thrown
        with pytest.raises(RuntimeError):
            sut.attach(self.client)


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeUserResource:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    def test_create(self, respx_mock):
        respx_mock.post("/identity/api/users").mock(
            return_value=httpx.Response(200, json={"id": "bcdef"})
        )
        # given a desired user
        sut = identity.UserResource(
            id="user",
            login="match",
            first_name="Jess",
            last_name="Blofeldt",
            email_address="jess@blo.com",
            type=identity.UserType.SERVICE,
        )
        # when we create
        sut.create(self.client)
        # then the request is made
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/identity/api/users"
        assert json.loads(request.content) == {
            "login": "match",
            "firstName": "Jess",
            "lastName": "Blofeldt",
            "emailAddress": "jess@blo.com",
            "type": "Service",
        }
        # and the user gets an id
        assert sut.user_id == "bcdef"

    def test_deps(self):
        # given a desired user
        sut = identity.UserResource(
            id="user",
            login="match",
            first_name="Jess",
            last_name="Blofeldt",
            email_address="jess@blo.com",
            type=identity.UserType.SERVICE,
        )
        # it has no dependencies
        assert sut.deps() == []

    def test_update_with_change(self, respx_mock):
        # given a user in the remote
        respx_mock.get("/identity/api/users/xxyyzz").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "xxyyzz",
                    "login": "login@login.com",
                    "firstName": "Jess",
                    "lastName": "Blofeldt",
                    "emailAddress": "jess@blo.com",
                    "type": "Service",
                    "status": "active",
                },
            )
        )
        respx_mock.put("/identity/api/users/xxyyzz").mock(return_value=httpx.Response(200, json={}))
        # and existing state
        old_state = SimpleNamespace(id="22", userId="xxyyzz")
        # and desired state with a different firstname
        sut = identity.UserResource(
            id="22",
            login="login@login.com",
            first_name="New Jess",
            last_name="Blofeldt",
            email_address="jess@blo.com",
            type=identity.UserType.SERVICE,
        )
        # when we update
        new_state = sut.update(self.client, old_state)
        # then the request is made
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/identity/api/users/xxyyzz"
        assert json.loads(request.content) == {
            "login": "login@login.com",
            "firstName": "New Jess",
            "lastName": "Blofeldt",
            "emailAddress": "jess@blo.com",
            "type": "Service",
        }
        # and the new state is returned (the same as before)
        assert new_state is not None
        assert new_state["userId"] == "xxyyzz"

    def test_update_with_no_change(self, respx_mock):
        # given a user in the remote
        respx_mock.get("/identity/api/users/xxyyzz").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "xxyyzz",
                    "login": "login@login.com",
                    "firstName": "Jess",
                    "lastName": "Blofeldt",
                    "emailAddress": "jess@blo.com",
                    "type": "Service",
                    "status": "active",
                    "external": False,
                },
            )
        )
        # and existing state
        old_state = SimpleNamespace(id="22", userId="xxyyzz")
        # and desired state which is the same as the remote
        sut = identity.UserResource(
            id="22",
            login="login@login.com",
            first_name="Jess",
            last_name="Blofeldt",
            email_address="jess@blo.com",
            type=identity.UserType.SERVICE,
        )
        # when we update
        new_state = sut.update(self.client, old_state)
        # the new state is None
        assert new_state is None
        # and no put request is made

    def test_update_cannot_change_login(self, respx_mock):
        # given a user in the remote
        respx_mock.get("/identity/api/users/xxyyzz").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "xxyyzz",
                    "login": "login@login.com",
                    "firstName": "Jess",
                    "lastName": "Blofeldt",
                    "emailAddress": "jess@blo.com",
                    "type": "Service",
                    "status": "active",
                    "external": False,
                },
            )
        )
        # and existing state
        old_state = SimpleNamespace(id="22", userId="xxyyzz")
        # and desired state with a different login
        sut = identity.UserResource(
            id="22",
            login="different_login@login.com",
            first_name="Jess",
            last_name="Blofeldt",
            email_address="jess@blo.com",
            type=identity.UserType.SERVICE,
        )
        with pytest.raises(RuntimeError):
            sut.update(self.client, old_state)

    def test_delete(self, respx_mock):
        respx_mock.delete("/identity/api/users/xxyyzz").mock(return_value=httpx.Response(200, json={}))
        # given a role that exists
        old_state = SimpleNamespace(userId="xxyyzz", id="res_id")
        # when we delete it
        identity.UserResource.delete(self.client, old_state)
        # then a delete request is sent with the userId
        request = respx_mock.calls.last.request
        assert request.method == "DELETE"
        assert request.url.path == "/identity/api/users/xxyyzz"


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeRoleAssignment:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    @pytest.fixture
    def created_role(self, respx_mock):
        respx_mock.post("/identity/api/roles").mock(
            return_value=httpx.Response(
                200, json={"id": "role01", "roleId": {"scope": "default", "code": "role1"}}
            )
        )
        # given a desired role
        role = identity.IdentityRoleResource(id="role_id", name="role1", description="role one")
        role.create(self.client)
        return role

    @pytest.fixture
    def created_user(self, respx_mock):
        respx_mock.post("/identity/api/users").mock(
            return_value=httpx.Response(200, json={"id": "user02"})
        )
        user = identity.UserResource(
            id="user",
            login="match",
            first_name="Jess",
            last_name="Blofeldt",
            email_address="jess@blo.com",
            type=identity.UserType.SERVICE,
        )
        user.create(self.client)
        return user

    def test_create(self, respx_mock, created_user, created_role):
        respx_mock.put("/identity/api/roles/role01/users/user02").mock(
            return_value=httpx.Response(200, json={})
        )
        # given a user and a role
        # and the desired assignment
        sut = identity.RoleAssignment(id="ass1", user=created_user, role=created_role)
        # when we create
        sut.create(self.client)
        # then the request is made
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/identity/api/roles/role01/users/user02"

    def test_create_with_user_ref(self, respx_mock, created_role):
        respx_mock.get("/identity/api/users").mock(
            return_value=httpx.Response(200, json=[{"id": "user02", "login": "match"}])
        )
        user_ref = identity.UserRef(id="user", login="match")
        user_ref.attach(self.client)

        respx_mock.put("/identity/api/roles/role01/users/user02").mock(
            return_value=httpx.Response(200, json={})
        )

        # given a user ref and a role
        # and the desired assignment
        sut = identity.RoleAssignment(id="ass1", user=user_ref, role=created_role)
        # when we create
        sut.create(self.client)
        # then the request is made
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/identity/api/roles/role01/users/user02"

    def test_update_no_change(self, respx_mock, created_user, created_role):
        # gvien an assignment which matches the remote
        sut = identity.RoleAssignment(id="ass1", user=created_user, role=created_role)
        # when we update
        old_state = SimpleNamespace(id="ass1", roleId="role01", userId="user02")
        new_state = sut.update(self.client, old_state)
        # the new state is none
        assert new_state is None
        # and no put request is made

    def test_update_change_user_when_remote_exists(self, respx_mock, created_user, created_role):
        respx_mock.put("/identity/api/roles/role01/users/user02").mock(
            return_value=httpx.Response(200, json={})
        )
        respx_mock.delete("/identity/api/roles/role01/users/user01").mock(
            return_value=httpx.Response(200, json={})
        )
        # given the existing remote is for user01
        old_state = SimpleNamespace(id="ass1", roleId="role01", userId="user01")
        # and a desired state of user02
        sut = identity.RoleAssignment(id="ass1", user=created_user, role=created_role)
        # when we update
        new_state = sut.update(self.client, old_state)
        # then the new state is user02
        assert new_state == {"id": "ass1", "roleId": "role01", "userId": "user02"}
        # and the existing assignment is deleted
        request = respx_mock.calls[-2].request
        assert request.method == "DELETE"
        assert request.url.path == "/identity/api/roles/role01/users/user01"
        # and a new one is created
        request = respx_mock.calls[-1].request
        assert request.method == "PUT"
        assert request.url.path == "/identity/api/roles/role01/users/user02"

    def test_deps(self, created_user, created_role):
        # given a desired assignment
        sut = identity.RoleAssignment(id="ass1", user=created_user, role=created_role)
        # it depends on the user and the role
        assert sut.deps() == [created_user, created_role]
        ref = identity.UserRef(id="user", login="match")
        sut = identity.RoleAssignment(id="ass1", user=ref, role=created_role)
        assert sut.deps() == [ref, created_role]

    def test_delete(self, respx_mock, created_user, created_role):
        respx_mock.delete("/identity/api/roles/role01/users/user02").mock(
            return_value=httpx.Response(200, json={})
        )
        # given an existing remote
        old_state = SimpleNamespace(id="ass1", roleId="role01", userId="user02")
        # when we delete it
        identity.RoleAssignment.delete(self.client, old_state)
        # the existing assignment is deleted
        request = respx_mock.calls[-1].request
        assert request.method == "DELETE"
        assert request.url.path == "/identity/api/roles/role01/users/user02"
