var vm = new Vue({
    el: '#app',
    data: {
        username_error_flag: false,
        image_code_error_flag: false,
        usernsme_error_flag: false,
        first_step: true,
        second_step: false,
        thired_step: false,
        password2_error_flag: false,
        password_error_flag: false,
        fouth_step: false,
        hosts,
        image_code_url:'',
        uuid:'',
        mobile:'',
        image_code_text:'',
        usernsme_error:'',
        image_code_error:'验证码错误',
        step_classobj:'step step-1',
        mobile_forbidden:'',
        access_token:'',
        sms_status: '发送验证码',
        sms_error_flag: false,
        sms_error:'',
        mobile_to_oauth:'',
        sms_code:'',
        mobile_error:'',
        user_id:'',
        password: '',
        password2: '',
        password2_error:'',
        password_error:'',



    },
    mounted: function () {
        this.generate_image_url()
    },
    methods: {
        check_username:function () {
            if(this.mobile.length<5||this.mobile.length>20){
                this.usernsme_error_flag=true
                this.usernsme_error='输入5~20个字符的用户名'
            }else{
                this.usernsme_error_flag=false
            }
        },
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
        generate_image_url: function () {
            this.uuid=this.generateUUID()
            this.image_code_url=this.hosts+"/image_code/"+this.uuid+"/"

        },
        check_image_code:function(){
        if(this.mobile&&this.image_code_text) {
            this.image_code_error_flag = false
        }else{
            this.image_code_error_flag = true
        }
            // axios.get(this.hosts + "/smscode/" + this.mobile + "/?text=" +
            //     this.image_code_text + "&uuid=" + this.uuid, {
            //     responseType: 'json'
            //
            // }).then(response => {
            //     this.image_code_error_flag = false
            //     console.log(response.data)
            // }).catch(error => {
            //     this.image_code_error_flag = true
            // })
        },
        on_submit_first: function () {

            if(!this.image_code_error_flag&&!this.username_error_flag&&this.mobile&&this.image_code_text){
            // 传入手机号
            // GET accounts/(?P<account>\w{5,20})/sms/token/
            axios.get(this.hosts+"/accounts/"+this.mobile+"/sms/token/?text="
                +this.image_code_text+'&uuid='+this.uuid,{
                responseType:'json'
            }).then(response=>{
                //返回了access_token要保存
                sessionStorage.clear()
                sessionStorage.access_token=response.data.access_token
                sessionStorage.mobile=response.data.mobile
                this.step_classobj='step step-2'
                this.first_step=false
                this.second_step=true
                this.mobile_forbidden=response.data.mobile
            }).catch(error=>{
                if(error.response.status==404){
                    this.image_code_error='用户不存在!'
                    this.image_code_error_flag=true
                }else if(error.response.status==400){
                    this.image_code_error='验证码过期!'
                    this.image_code_error_flag=true
                }else if(error.response.status==401){
                    this.image_code_error='验证码错误!'
                    this.image_code_error_flag=true
                }
            })

        }
        },
        send_sms_code:function () {
            this.access_token=sessionStorage.access_token
            axios.get(this.hosts+"/sms_codes/?access_token="+this.access_token,{
                responseType:'json'
            }).then(response=>{
                console.log(response.data)
                var num = 60;
                var t = setInterval(() => {
                    if (num != 0) {
                        this.sms_status = num + '秒'
                        // $(".get_code").show()
                        num -= 1;
                    } else {
                        clearInterval(t)
                        this.sms_status = '获取短信验证码';
                    }
                }, 1000, 60);
            }).catch(error=>{
                this.sms_error='短信密码错误!'
            })
        },
        on_submit_second:function(){
                // accounts/(?P<account>\w{5,20})/password/token/?sms_code=

            this.mobile_to_oauth=sessionStorage.mobile
            axios.get(this.hosts+"/accounts/"+this.mobile+
                "/password/token/?sms_code="+this.sms_code,{
                responseType:'json'
            }).then(response=>{
                this.second_step=false
                this.thired_step=true
                this.step_classobj='step step-3'
                sessionStorage.clear()
                sessionStorage.access_token=response.data.access_token
                sessionStorage.user_id=response.data.user_id
            }).catch(error=>{
                if(error.response.status==400){
                    this.sms_error='短信验证码过期'
                    this.sms_error_flag=true

                }else if(error.response.status==401){
                    this.sms_error='短信验证码输入错误'
                    this.sms_error_flag=true
                }else if(error.response.status==404){
                    this.sms_error='没有找到用户'
                    this.sms_error_flag=true
                }
            })
        },
        check_mobile_forbiden: function () {
            if(this.mobile_forbidden==1){
                this.mobile_error='手机号错误'
            }
        },
        on_submit_thired: function () {
            // users/(?P<pk>\d+)/password/?access_token=xxx
            this.user_id=sessionStorage.user_id
            this.access_token=sessionStorage.access_token
            axios.post(this.hosts+"/users/"+this.user_id+"/password/",{
                access_token:this.access_token,
                password:this.password,
                password2:this.password,
            },{
            responseType:'json'
            }).then(response=>{
                // console.log(response.data)
                this.step_classobj='step step-4'
                this.thired_step=false
                this.fouth_step=true
            }).catch(error=>{
                alert('wrong')
            })

        },
        check_password:function () {
            // 判断2次输入的密码一致
            if(this.password!=this.password2){
                this.password2_error_flag=true
                this.password2_error='两次输入的密码不一致'
            }
        },
        password_first_blur:function () {
            if(this.password.length<5||this.password.length>20){
                this.password_error='密码必须为5~20个字符'
                this.password_error_flag=true
            }
        }


    },


})