var vm = new Vue({
    el: '#app',
    data: {
        username_erro_flag: false,
        password_erro_flag: false,

        user_name: '',
        password: '',
        hosts,
        remember: false,
        username_erro: '请输入5-20个字符的用户',
        password_erro: '请输入8~20位的密码',
    },
    methods: {
        username_check: function () {
            if (this.user_name.length < 5 || this.user_name.length > 20) {
                this.username_erro_flag = true
            }
            else {
                this.username_erro_flag = false
            }
        },
        passwd_check: function () {
            if (this.password.length < 8 || this.password.length > 20) {
                this.password_erro_flag = true
            } else {
                this.password_erro_flag = false
            }
        },
        get_query_string: function (name) {
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
        on_submit: function () {
            axios.post(this.hosts + "/authorizations/", {
                username: this.user_name,
                password: this.password,
            }, {
                responseType: "json"

            }).then(response => {

                if (this.remember) {
                    sessionStorage.clear()
                    localStorage.token = response.data.token
                    localStorage.user_id = response.data.user_id
                    localStorage.username = response.data.username

                } else {
                    localStorage.clear()
                    sessionStorage.token = response.data.token
                    sessionStorage.user_id = response.data.token
                    sessionStorage.username = response.data.username
                }

                //跳转页面
                var return_url = this.get_query_string('next');
                if (!return_url) {
                    return_url = '/index.html';
                }
                location.href = return_url;
            }).catch(erro => {
                this.password_erro_flag = true
                this.password_erro = '用户名或者密码错误'

            })
        },
        qq_login: function () {
            // GET /oauth/qq/authorization/
            state = this.get_query_string('state')
            axios.get(this.hosts + "/oauth/qq/authorization/?state=" + state, {
                responseType: 'json'
            }).then(response => {
                url = response.data.url
                location.href = url
            }).catch(error => {
                console.log(error.response.data);
            })
        },

    },

})