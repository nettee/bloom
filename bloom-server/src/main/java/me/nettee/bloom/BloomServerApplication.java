package me.nettee.bloom;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;

@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
public class BloomServerApplication {

	public static void main(String[] args) {
		SpringApplication.run(BloomServerApplication.class, args);
	}

}
