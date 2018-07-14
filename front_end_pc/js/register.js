var vm = new Vue({
    el: '#app',
    data: {
        error_name: false,
        error_password: false,
        error_check_password: false,
        error_phone: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code: false,

        username: '',
        password: '',
        password2: '',
        mobile: '',
        image_code: '',
        sms_code: '',
        allow: false,
        image_code_id: '',
        image_code_url: '',
        sms_status: '获取短信验证码',
        hosts,
    },

    // 钩子

    mounted: function () {
        // 在页面加载之前请求一个验证码
        // TODO 发起请求
        this.image_code_id = this.generateUUID()
        this.image_code_url = this.hosts+"/image_code/" + this.image_code_id + "/"

    },
    methods: {
        // 生成uuid
        generateUUID: function () {
            var d = new Date().getTime();
            if (window.performance && typeof window.performance.now === "function") {
                d += performance.now(); //use high-precision timer if available
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                var r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return uuid;
        },
        // 每次点击验证码时候,更换验证码
        change_image_code: function () {
            this.image_code_id = this.generateUUID()
            this.image_code_url = this.hosts+"/image_code/" + this.image_code_id + "/"
        },


        check_username: function () {
            var len = this.username.length;
            if (len < 5 || len > 20) {
                this.error_name = true;
            } else {
                this.error_name = false;
            }
        },
        check_pwd: function () {
            var len = this.password.length;
            if (len < 8 || len > 20) {
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        check_cpwd: function () {
            if (this.password != this.password2) {
                this.error_check_password = true;
            } else {
                this.error_check_password = false;
            }
        },
        check_phone: function () {
            var re = /^1[345789]\d{9}$/;
            if (re.test(this.mobile)) {
                this.error_phone = false;
            } else {
                this.error_phone = true;
            }
        },
        check_image_code: function () {
            if (!this.image_code) {
                this.error_image_code = true;
            } else {
                this.error_image_code = false;
            }
            ;
            // 验证码的验证
        },
        check_sms_code: function () {
            if (!this.sms_code) {
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },// TODO 获取短信验证码
        getSMScode: function () {

            axios.get(this.hosts+"/smscode/" + this.mobile + "/?text=" +
                this.image_code + "&uuid=" + this.image_code_id, {
                responseType: 'json'

            }).then(response =>{
                // 倒计时60s
                var num= 60;

                var t = setInterval(() => {
                    if (num != 0) {
                        this.sms_status=num+'秒'
                        // $(".get_code").show()
                        num -= 1;
                    } else {
                        clearInterval(t)
                        this.sms_status='获取短信验证码';

                    }
                }, 1000,60);




            })




},


check_allow: function () {
    if (!this.allow) {
        this.error_allow = true;
    } else {
        this.error_allow = false;
    }
}
,
// 注册
on_submit: function () {
    this.check_username();
    this.check_pwd();
    this.check_cpwd();
    this.check_phone();
    this.check_sms_code();
    this.check_allow();
}
}
})
;
