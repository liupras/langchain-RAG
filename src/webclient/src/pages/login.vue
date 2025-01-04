<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col md="4">
        <v-overlay :model-value="isLoading" class="justify-center align-center">
          <v-progress-circular
            indeterminate
            color="white"
          ></v-progress-circular>
        </v-overlay>
        <v-card class="pa-8 mx-auto">
          <v-card-title class="text-center">登录</v-card-title>
          <v-card-item>
            <v-sheet>
              <v-form @submit.prevent>
                <v-text-field
                  v-model="form_data.username"
                  label="电子邮件地址"
                  variant="solo"
                  prepend-inner-icon="mdi-email"
                  :rules="[rules.required, rules.username, rules.max]"
                ></v-text-field>
                <v-text-field
                  type="password"
                  v-model="form_data.password"
                  label="密码"
                  variant="solo"
                  prepend-inner-icon="mdi-key"
                  :rules="[rules.required, rules.max]"
                ></v-text-field>
                <v-container>
                  <v-row>
                    <v-text-field
                      v-model="form_data.capchaText"
                      label="输入验证码"
                      variant="solo"
                      :rules="[rules.required, rules.max]"
                    ></v-text-field
                    ><v-img
                      :src="imageSrc"
                      alt="验证码"
                      class="mb-4"
                      max-height="60"
                      @click="refreshCaptcha"
                      style="cursor: pointer"
                    >
                    </v-img>
                  </v-row>
                </v-container>
                <v-checkbox
                  v-model="form_data.remember"
                  color="red"
                  label="30天内免登录"
                  hide-details
                ></v-checkbox>
                <v-btn type="submit" color="primary" @click="submit" block>
                  <span>登录</span>
                </v-btn>
                <v-alert
                  closable
                  icon="mdi-alert-circle-outline"
                  :text="error_msg"
                  type="error"
                  v-if="error"
                ></v-alert>
              </v-form>
            </v-sheet>
          </v-card-item>
          <v-card-actions>
            <div class="mx-4">
              <v-btn block to="/regist">注册</v-btn>
            </div>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
    
<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { jwtDecode } from "jwt-decode";

import { setToken } from "@/assets/js/auth";

const login_url = "http://127.0.0.1:8000/token";
const capcha_url = "http://127.0.0.1:8000/captcha";

const imageSrc = ref("");

//表单数据
const form_data = ref({
  username: "",
  password: "",
  remember: false,
  capchaId: "",
  capchaText: "",
});

const isLoading = ref(false);
const error = ref(false);
const error_msg = ref("");

// 获取验证码
const fetchCaptcha = async () => {
  try {
    let img_url = capcha_url + "?t=" + Date.now();
    const response = await axios(img_url, { responseType: "blob" });  // 响应类型为 blob，非常重要！
    console.log("获取验证码成功:", response);

    form_data.value.capchaId = response.headers["x-captcha-id"]; // 验证码唯一标识符
    console.log("验证码ID:", form_data.value.capchaId);
    imageSrc.value = URL.createObjectURL(response.data);
  } catch (error) {
    console.log("获取验证码失败:", error);
    if (error.code == "ERR_NETWORK") {
      error_msg.value = "网络错误，无法连接到服务器。";
    } else {
      error_msg.value = error.response.data.detail;
    }
  }

  if (error_msg.value != "") {
    error.value = true;
  }
};

// 刷新验证码
const refreshCaptcha = () => {
  fetchCaptcha();
  form_data.value.capchaText = ""; // 清空用户输入
};

onMounted(() => {
  fetchCaptcha();
});

// 获取路由实例
import { useRoute, useRouter } from "vue-router";
const route = useRoute();
const router = useRouter();

const emits = defineEmits(["login"]);

//提交
async function submit() {
  if (
    form_data.value.username === "" ||
    form_data.value.password === "" ||
    form_data.value.capchaText === ""
  ) {
    return;
  }

  isLoading.value = true;
  error.value = false;
  error_msg.value = "";

  const formData = new FormData();
  formData.append("username", form_data.value.username);
  formData.append("password", form_data.value.password);
  formData.append("remember", form_data.value.remember);
  formData.append("captcha_id", form_data.value.capchaId);
  formData.append("captcha_input", form_data.value.capchaText);

  try {
    const response = await axios.post(login_url, formData, {
      headers: {
        "Content-Type": "multipart/form-data", // 指定使用 form-data 格式
      },
    });

    const token = response.data.access_token;
    //console.log(token);

    // 解析 JWT Token 内容
    const decodedToken = jwtDecode(token);
    console.log("解析后的 Token 内容:", decodedToken);

    // 存储token
    setToken(token);

    let userid = decodedToken["sub"];
    emits("login", userid);

    if (route.query && route.query["redirect"]) {
      router.push({ path: route.query["redirect"] });
    } else {
      router.push({ path: "/" });
    }
  } catch (error) {
    console.log("登录失败:", error);
    if (error.code == "ERR_NETWORK") {
      error_msg.value = "网络错误，无法连接到服务器。";
    } else {
      error_msg.value = error.response.data.detail;
    }
  }

  isLoading.value = false;
  if (error_msg.value != "") {
    error.value = true;
  }
}

//校验规则
const rules = {
  required: (value) => !!value || "不能为空。",
  max: (value) => value.length <= 20 || "最多20个字符。",
  username: (value) => {
    const pattern =
      /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return pattern.test(value) || "Invalid e-mail.";
  },
};
</script>