library ieee;
use IEEE.std_logic_1164.all;

entity S_mach is
port (clk : in std_logic;
      enable : in std_logic;
	  reset : in std_logic;
      first_byte : in std_logic;
      input_valid : in std_logic;
      last_byte : in std_logic;
      output_valid : out std_logic;
      ready_for_input : out std_logic;
	  init : out std_logic
  );
end S_mach;

architecture behavioral of S_mach is

type state_type is (ideal,F_byte,in_progress,L_byte);  --type of state machine.
signal current_s,next_s: state_type;  --current and next state declaration.

begin

process (clk,reset)
begin
 if (reset='1') then
  current_s <= ideal;  --default state on reset.
elsif (rising_edge(clk)) then
  current_s <= next_s;   --state change.
end if;
end process;

--state machine process.
process (current_s,first_byte,input_valid,last_byte,enable)
begin
if (enable = '1') then
  case current_s is
     when ideal =>        --when current state is "s0"
         if(first_byte = '1' ) then
          ready_for_input <= '1';
          output_valid <= '0';
		  init <= '1';
          next_s <= F_byte;
        else
          ready_for_input <= '0';
          output_valid <= '0';
          next_s <= ideal;
         end if;   

     when F_byte =>        --when current state is "s1"
	    init <= '0';
        if(input_valid = '1') then
          ready_for_input <= '1';
          output_valid <= '0';
          next_s <= in_progress;
        else
          ready_for_input <= '1';
          output_valid <= '0';
          next_s <= F_byte;
        end if;

    when in_progress =>       --when current state is "s2"
	    init <= '0';
        if(last_byte ='1') then
          ready_for_input <= '0';
          output_valid <= '1';
          next_s <= L_byte;
        else
          ready_for_input <= '1';
          output_valid <= '0';
          next_s <= in_progress;
        end if;


      when L_byte =>         --when current state is "s3"
        ready_for_input <= '0';
        output_valid <= '1';
		init <= '0';
        next_s <= ideal;
    
  end case;
  end if;
end process;

end behavioral;
